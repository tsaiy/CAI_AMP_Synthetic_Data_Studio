import sqlite3
from typing import Dict, List, Optional
import json
from datetime import datetime
import os
import time

class DatabaseManager:
    def __init__(self, db_path: str = "metadata.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get database connection with consistent settings"""
        conn = sqlite3.connect(self.db_path, timeout=60)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=60000')  # Increased timeout
        conn.execute('PRAGMA synchronous=FULL')    # Changed from NORMAL to FULL
        conn.execute('PRAGMA foreign_keys=ON')
        return conn

    def init_db(self):
        """Initialize database with required tables"""
        try:
            if os.path.exists(self.db_path):
                try:
                    with self.get_connection() as test_conn:
                        test_conn.execute("PRAGMA quick_check")
                except sqlite3.DatabaseError:
                    print("Detected corrupted database, recreating...")
                    if os.path.exists(self.db_path):
                        os.remove(self.db_path)
                    if os.path.exists(f"{self.db_path}-shm"):
                        os.remove(f"{self.db_path}-shm")
                    if os.path.exists(f"{self.db_path}-wal"):
                        os.remove(f"{self.db_path}-wal")

            with self.get_connection() as conn:
                
                
                cursor = conn.cursor()
                
                # Create tables with additional indexes for better query performance
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS generation_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        model_id TEXT,
                        inference_type TEXT,
                        use_case TEXT,
                        custom_prompt TEXT,
                        model_parameters TEXT,
                        generate_file_name TEXT UNIQUE,
                        display_name TEXT,
                        local_export_path TEXT,
                        hf_export_path TEXT,
                        num_questions FLOAT,
                        total_count FLOAT,
                        topics TEXT,
                        examples TEXT,
                        schema TEXT,
                        job_id TEXT,
                        job_name TEXT UNIQUE,
                        job_status TEXT
                       
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS evaluation_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        model_id TEXT,
                        inference_type TEXT,
                        use_case TEXT,
                        custom_prompt TEXT,
                        model_parameters TEXT,
                        generate_file_name TEXT,
                        evaluate_file_name TEXT UNIQUE,
                        display_name TEXT,
                        local_export_path TEXT,
                        examples TEXT,
                        average_score FLOAT,
                        job_id TEXT,
                        job_name TEXT UNIQUE,
                        job_status TEXT
                       
                    )
                """)
                
               
                
                conn.commit()
                print("Database initialized successfully")
    
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            # If all else fails, remove the database and try one final time
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                return self.init_db()  # One final retry
            raise
            

   
        
        
    def save_generation_metadata(self, metadata: Dict) -> int:
        """Save generation metadata to database with prepared transaction"""
        try:
            # Prepare data outside transaction
            if metadata.get('generate_file_name'):
                
                output_paths = metadata.get('output_path', {})
            else:
                
                output_paths = {}
                
            model_params_json = json.dumps(metadata.get('model_parameters', {}))
            topics_json = json.dumps(metadata.get('topics', []))
            examples_json = json.dumps(metadata.get('examples', []))
            
            display_name = (
                metadata.get('display_name') or 
                metadata.get('generate_file_name') or 
                None
            )
            
            # Use a single connection with enhanced settings
            with self.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                
                
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO generation_metadata (
                        timestamp, model_id, inference_type, use_case,
                        custom_prompt, model_parameters, generate_file_name,
                        display_name, local_export_path, hf_export_path,
                        num_questions, total_count, topics, examples,
                        schema, job_id, job_name, job_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    metadata.get('timestamp', None),
                    metadata.get('model_id', None),
                    metadata.get('inference_type', None),
                    metadata.get('use_case', None),
                    metadata.get('final_prompt', None),
                    model_params_json,
                    metadata.get('generate_file_name', None),
                    display_name,
                    output_paths.get('local', None),
                    output_paths.get('huggingface', None),
                    metadata.get('num_questions', None),
                    metadata.get('total_count', None),
                    topics_json,
                    examples_json,
                    metadata.get('schema', None),
                   
                    metadata.get('job_id', None),
                    metadata.get('job_name', None),
                    metadata.get('job_status', None)
                )
                
                cursor.execute(query, values)
                conn.commit()
                return cursor.lastrowid
                
        except sqlite3.OperationalError as e:
            if conn:
                conn.rollback()
            print(f"Database operation error in save_generation_metadata: {e}")
            
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error saving metadata to database: {str(e)}")
            raise

    def update_job_generate(self, job_name: str, generate_file_name: str, local_export_path: str, timestamp: str, job_status):
        """Update job generate with retry mechanism"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    conn.execute("BEGIN IMMEDIATE")
                    
                    cursor = conn.cursor()
                    
                    # First check if the row exists and is ready for update
                    cursor.execute("""
                        SELECT COUNT(*) FROM generation_metadata 
                        WHERE job_name = ? AND job_name IS NOT NULL AND job_name != ''
                    """, (job_name,))
                    
                    if cursor.fetchone()[0] == 0:
                        print(f"No record found for job name: {job_name}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        else:
                            raise ValueError(f"No record found for job name: {job_name} after {max_retries} attempts")
                    
                    # Perform the update
                    cursor.execute("""
                        UPDATE generation_metadata 
                        SET generate_file_name = ?,
                            local_export_path = ?,
                            timestamp = ?,
                            job_status = ?
                        WHERE job_name = ?
                        AND job_name IS NOT NULL 
                        AND job_name != ''
                    """, (generate_file_name, local_export_path, timestamp, job_status, job_name))
                    
                    rows_affected = cursor.rowcount
                    conn.commit()
                    
                    if rows_affected > 0:
                        print(f"Successfully updated file paths for job: {job_name}")
                        return True
                        
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Database locked, attempt {attempt + 1} of {max_retries}")
                    time.sleep(retry_delay)
                    if conn:
                        conn.rollback()
                    continue
                else:
                    print(f"Database operation error in update_job_generate: {e}")
                    if conn:
                        conn.rollback()
                    raise
            except Exception as e:
                if conn:
                    conn.rollback()
                print(f"Error updating file paths: {str(e)}")
                raise
    
        raise Exception(f"Failed to update job after {max_retries} attempts")




    
    
    def save_evaluation_metadata(self, metadata: Dict) -> int:
        """Save evaluation metadata to database with improved locking handling"""
        try:
            # Prepare data outside transaction
            
            
            model_params_json = json.dumps(metadata.get('model_parameters', {}))
            examples_json = json.dumps(metadata.get('examples', []))
            
            try:
                avg_score = round(float(metadata.get('Overall_Average', 0)), 2)
            except (TypeError, ValueError):
                avg_score = None
                
            display_name = (
                metadata.get('display_name') or 
                metadata.get('generate_file_name') or 
                None
            )
            
            with self.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                
                
                cursor = conn.cursor()
                
                query = """
                    INSERT INTO evaluation_metadata (
                        timestamp, model_id, inference_type, use_case,
                        custom_prompt, model_parameters, generate_file_name,
                        evaluate_file_name, display_name, local_export_path,
                        examples, average_score, job_id, job_name, job_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    metadata.get('timestamp', None),
                    metadata.get('model_id'),
                    metadata.get('inference_type'),
                    metadata.get('use_case'),
                    metadata.get('custom_prompt'),
                    model_params_json,
                    metadata.get('generate_file_name'),
                    metadata.get('evaluate_file_name'),
                    display_name,
                    metadata.get('local_export_path', None),
                    examples_json,
                    avg_score,
                   
                    metadata.get('job_id', None),
                 metadata.get('job_name', None),
                    metadata.get('job_status', None)
                )
                
                cursor.execute(query, values)
                conn.commit()
                return cursor.lastrowid
                
        except sqlite3.OperationalError as e:
            print(f"Database operation error in save_evaluation_metadata: {e}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            print(f"Error saving evaluation metadata: {str(e)}")
            if conn:
                conn.rollback()
            raise

    def update_job_evaluate(self, job_name: str, evaluate_file_name: str, local_export_path: str, timestamp: str, average_score: float, job_status:str):
        """Update job evaluation with retry mechanism"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                with self.get_connection() as conn:
                    conn.execute("BEGIN IMMEDIATE")
                    
                    
                    cursor = conn.cursor()
                    
                    # Check if row exists first
                    cursor.execute("""
                        SELECT COUNT(*) FROM evaluation_metadata 
                        WHERE job_name = ? AND job_name IS NOT NULL AND job_name != ''
                    """, (job_name,))
                    
                    if cursor.fetchone()[0] == 0:
                        print(f"No evaluation record found for job name: {job_name}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        else:
                            raise ValueError(f"No evaluation record found for job name: {job_name} after {max_retries} attempts")
                    
                    # Perform the update
                    cursor.execute("""
                        UPDATE evaluation_metadata 
                        SET evaluate_file_name = ?,
                            local_export_path = ?,
                            timestamp = ?,
                            average_score = ?,
                            job_status = ?
                        WHERE job_name = ?
                        AND job_name IS NOT NULL 
                        AND job_name != ''
                    """, (evaluate_file_name, local_export_path, timestamp, average_score, job_status, job_name))
                    
                    rows_affected = cursor.rowcount
                    conn.commit()
                    
                    if rows_affected > 0:
                        print(f"Successfully updated evaluation for job: {job_name}")
                        return True
                        
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"Database locked, attempt {attempt + 1} of {max_retries}")
                    time.sleep(retry_delay)
                    continue
                else:
                    if conn:
                        conn.rollback()
                    print(f"Database operation error in update_job_evaluate: {e}")
                    raise
            except Exception as e:
                if conn:
                    conn.rollback()
                print(f"Error updating evaluation file paths: {str(e)}")
                raise
        
        raise Exception(f"Failed to update evaluation job after {max_retries} attempts")
                

    def get_metadata_by_filename(self, file_name: str) -> Optional[Dict]:
        """Retrieve metadata by filename"""
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Changed from file_name to generate_file_name to match your table schema
                query = "SELECT * FROM generation_metadata WHERE generate_file_name = ?"
                cursor.execute(query, (file_name,))
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    result['model_parameters'] = json.loads(result['model_parameters'])
                    result['topics'] = json.loads(result['topics'])
                    result['examples'] = json.loads(result['examples'])
                    conn.rollback()
                    return result
                return None
                
        except Exception as e:
            print(f"Error retrieving metadata: {str(e)}")
            return None

    def get_all_generate_metadata(self) -> List[Dict]:
        """Retrieve all metadata entries"""
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM generation_metadata ORDER BY timestamp DESC"
                cursor.execute(query)
                
                results = []
                for row in cursor.fetchall():
                    result = dict(row)
                    result['model_parameters'] = json.loads(result['model_parameters'])
                    result['topics'] = json.loads(result['topics'])
                    result['examples'] = json.loads(result['examples'])
                    results.append(result)
                #print(results)
                conn.rollback()
                return results
                
        except Exception as e:
            print(f"Error retrieving all metadata: {str(e)}")
            return []
        
    def get_all_evaluate_metadata(self) -> List[Dict]:
        """Retrieve all metadata entries"""
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM evaluation_metadata ORDER BY timestamp DESC"
                cursor.execute(query)
                
                results = []
                for row in cursor.fetchall():
                    result = dict(row)
                    result['model_parameters'] = json.loads(result['model_parameters'])
                    result['examples'] = json.loads(result['examples'])
                    results.append(result)
                conn.rollback()
                return results
                
        except Exception as e:
            print(f"Error retrieving all metadata: {str(e)}")
            return []

    def get_evaldata_by_filename(self, file_name: str) -> Optional[Dict]:
        """Retrieve metadata by filename"""
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Changed from file_name to generate_file_name to match your table schema
                query = "SELECT * FROM evaluation_metadata WHERE evaluate_file_name = ?"
                cursor.execute(query, (file_name,))
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    result['model_parameters'] = json.loads(result['model_parameters'])
                    
                    result['examples'] = json.loads(result['examples'])
                    conn.rollback()
                    return result
                return None
                
        except Exception as e:
            print(f"Error retrieving metadata: {str(e)}")
            return None

    def update_generate_display_name(self, file_name: str, display_name: str):
        """Update display name for a generation"""
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cursor = conn.cursor()
                
                # Check for duplicate display name
                cursor.execute(
                    "SELECT COUNT(*) FROM generation_metadata WHERE generate_display_name = ? AND generate_file_name != ?",
                    (display_name, file_name)
                )
                count = cursor.fetchone()[0]
                
                if count > 0:
                    raise ValueError(f"Display name '{display_name}' already exists")
                
                # Update the display name
                cursor.execute(
                    "UPDATE generation_metadata SET generate_display_name = ? WHERE generate_file_name = ?",
                    (display_name, file_name)
                )
                conn.commit()
                print(f"Update successful for file: {file_name}")
        except Exception as e:
            print(f"Error updating display name: {str(e)}")
            raise

    


    def update_evaluate_display_name(self, file_name: str, display_name: str):
        """Update display name for evaluation"""
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cursor = conn.cursor()
                
                # Check for duplicate display name
                cursor.execute(
                    "SELECT COUNT(*) FROM evaluation_metadata WHERE evaluate_display_name = ? AND evaluate_file_name != ?",
                    (display_name, file_name)
                )
                count = cursor.fetchone()[0]
                
                if count > 0:
                    raise ValueError(f"Display name '{display_name}' already exists")
                
                # Update the display name
                cursor.execute(
                    "UPDATE evaluation_metadata SET evaluate_display_name = ? WHERE evaluate_file_name = ?",
                    (display_name, file_name)
                )
                conn.commit()
                print(f"Update successful for file: {file_name}")
        except Exception as e:
            print(f"Error updating evaluation display name: {str(e)}")
            raise


    def delete_generate_data(self,file_name:str, file_path: Optional[str] = None ):
        
        try:
            if file_path and os.path.exists(file_path):
                #file_name = os.path.basename(file_path)
                os.remove(file_path)
            with self.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cursor = conn.cursor()
                cursor.execute(
                    "Delete from generation_metadata  WHERE generate_file_name = ?",
                    (file_name,)
                )
                conn.commit()
                
        except Exception as e:
            print(f"Error deleting generation metadata: {str(e)}")
            raise

    def delete_evaluate_data(self,file_name:str, file_path: Optional[str] = None):
       
        try:
            if file_path and os.path.exists(file_path):
                #file_name = os.path.basename(file_path)
                os.remove(file_path)
            
            with self.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cursor = conn.cursor()
                cursor.execute(
                    "Delete from evaluation_metadata  WHERE evaluate_file_name = ?",
                    (file_name,)
                )
                conn.commit()
                
        except Exception as e:
            print(f"Error deleting evaluation metadata: {str(e)}")
            raise

    def update_hf_path(self, file_name: str, hf_path: str):
        """Update display name for a generation"""
        try:
            with self.get_connection() as conn:
                conn.execute("BEGIN IMMEDIATE")
                cursor = conn.cursor()
              
                
                # Update the hf_path
                cursor.execute(
                    "UPDATE generation_metadata SET hf_export_path = ? WHERE generate_file_name = ?",
                    (hf_path, file_name)
                )
                conn.commit()
                print(f"Update successful for file: {file_name}")
        except Exception as e:
            print(f"Error updating display name: {str(e)}")
            raise
    def backup_and_restore_db(self, force_restore: bool = False) -> bool:
        """
        Backup the current database, delete it, and restore from the backup.
        Uses consistent connection settings from get_connection().
        
        Args:
            force_restore (bool): If True, forces restore even if backup creation fails
            
        Returns:
            bool: True if successful, False otherwise
        """
        backup_path = f"{self.db_path}.backup"
        
        try:
            # Close all existing connections and checkpoint WAL
            with self.get_connection() as conn:
                conn.execute("PRAGMA wal_checkpoint(FULL)")
            
            # Create backup with consistent connection settings
            print("Creating database backup...")
            source_conn = self.get_connection()
            backup_conn = sqlite3.connect(backup_path, timeout=60)
            backup_conn.execute('PRAGMA journal_mode=WAL')
            backup_conn.execute('PRAGMA busy_timeout=60000')
            backup_conn.execute('PRAGMA synchronous=FULL')
            backup_conn.execute('PRAGMA foreign_keys=ON')
            
            with backup_conn:
                source_conn.backup(backup_conn)
            source_conn.close()
            backup_conn.close()
            print(f"Backup created at {backup_path}")
            
            # Delete existing database files
            print("Removing existing database...")
            files_to_remove = [
                self.db_path,
                f"{self.db_path}-shm",
                f"{self.db_path}-wal"
            ]
            
            for file in files_to_remove:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                    except PermissionError:
                        print(f"Permission error deleting {file}. Waiting for locks to clear...")
                        time.sleep(1)
                        os.remove(file)
            
            # Restore from backup using consistent connection settings
            print("Restoring from backup...")
            restore_source = sqlite3.connect(backup_path, timeout=60)
            restore_source.execute('PRAGMA journal_mode=WAL')
            restore_source.execute('PRAGMA busy_timeout=60000')
            restore_source.execute('PRAGMA synchronous=FULL')
            restore_source.execute('PRAGMA foreign_keys=ON')
            
            restore_dest = self.get_connection()
            
            with restore_dest:
                restore_source.backup(restore_dest)
            
            restore_source.close()
            restore_dest.close()
            
            # Remove backup file
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
            print("Database successfully restored")
            return True
            
        except Exception as e:
            print(f"Error during backup/restore: {str(e)}")
            if force_restore and os.path.exists(backup_path):
                print("Force restore requested, attempting to restore from backup...")
                try:
                    if os.path.exists(self.db_path):
                        os.remove(self.db_path)
                    restore_source = sqlite3.connect(backup_path, timeout=60)
                    restore_source.execute('PRAGMA journal_mode=WAL')
                    restore_source.execute('PRAGMA busy_timeout=60000')
                    restore_source.execute('PRAGMA synchronous=FULL')
                    restore_source.execute('PRAGMA foreign_keys=ON')
                    
                    restore_dest = self.get_connection()
                    
                    with restore_dest:
                        restore_source.backup(restore_dest)
                    restore_source.close()
                    restore_dest.close()
                    os.remove(backup_path)
                    return True
                except Exception as restore_error:
                    print(f"Force restore failed: {str(restore_error)}")
            return False
    
        
