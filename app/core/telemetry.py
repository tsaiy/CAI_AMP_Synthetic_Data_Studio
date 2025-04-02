import time
import uuid
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

# Configure logger
logger = logging.getLogger("telemetry")
logger.setLevel(logging.INFO)

# Create handlers for both file and console output
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
telemetry_log_file = log_dir / "telemetry.log"
telemetry_error_file = log_dir / "telemetry_errors.log"

file_handler = logging.FileHandler(telemetry_log_file)
file_handler.setLevel(logging.INFO)
error_handler = logging.FileHandler(telemetry_error_file)
error_handler.setLevel(logging.ERROR)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Create formatter and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

class TelemetryManager:
    """
    TelemetryManager provides methods to record and analyze application telemetry data.
    It stores data in SQLite for analysis and generates logs for real-time monitoring.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TelemetryManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.db_path = Path(__file__).parent.parent.parent / "telemetry.db"
        self._init_db()
        
        # In-memory queue for batch processing
        self.event_queue = []
        self.queue_lock = threading.Lock()
        self.max_queue_size = 100
        
        # Start background thread for batch processing
        self.batch_thread = threading.Thread(target=self._batch_processor, daemon=True)
        self.batch_thread.start()
        
        # Track if we're in a CML environment
        self.is_cml = os.getenv("CDSW_PROJECT_ID", "local") != "local"
        self.project_id = os.getenv("CDSW_PROJECT_ID", "local")
        
        logger.info(f"Telemetry manager initialized with database at {self.db_path}")
    
    def _init_db(self):
        """Initialize the SQLite database with required tables"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # API requests table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_requests (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    endpoint TEXT,
                    method TEXT,
                    status_code INTEGER,
                    response_time_ms REAL,
                    user_agent TEXT,
                    ip_address TEXT,
                    request_size INTEGER,
                    response_size INTEGER,
                    error TEXT
                )
                ''')
                
                # LLM operations table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS llm_operations (
                    id TEXT PRIMARY KEY,
                    request_id TEXT,
                    timestamp TEXT,
                    model_id TEXT,
                    operation_type TEXT,
                    tokens_input INTEGER,
                    tokens_output INTEGER,
                    latency_ms REAL,
                    success BOOLEAN,
                    error TEXT,
                    inference_type TEXT,
                    FOREIGN KEY (request_id) REFERENCES api_requests (id)
                )
                ''')
                
                # Job metrics table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_metrics (
                    id TEXT PRIMARY KEY,
                    request_id TEXT,
                    job_id TEXT,
                    timestamp_start TEXT,
                    timestamp_end TEXT,
                    job_type TEXT,
                    status TEXT,
                    memory_mb INTEGER,
                    cpu_cores INTEGER,
                    input_size INTEGER,
                    output_size INTEGER,
                    error TEXT,
                    FOREIGN KEY (request_id) REFERENCES api_requests (id)
                )
                ''')
                
                # System metrics table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    active_requests INTEGER
                )
                ''')
                
                # User interactions table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    session_id TEXT,
                    interaction_type TEXT,
                    details TEXT
                )
                ''')
                
                conn.commit()
                logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing telemetry database: {str(e)}")
    
    @contextmanager
    def _get_db_connection(self):
        """Get a connection to the SQLite database"""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def _batch_processor(self):
        """Background thread that processes the event queue in batches"""
        while True:
            time.sleep(5)  # Process every 5 seconds
            with self.queue_lock:
                if not self.event_queue:
                    continue
                
                # Process current batch
                batch = self.event_queue.copy()
                self.event_queue.clear()
            
            try:
                with self._get_db_connection() as conn:
                    cursor = conn.cursor()
                    
                    for event in batch:
                        table = event.pop('table')
                        keys = ', '.join(event.keys())
                        placeholders = ', '.join(['?' for _ in event.keys()])
                        values = tuple(event.values())
                        
                        query = f"INSERT OR REPLACE INTO {table} ({keys}) VALUES ({placeholders})"
                        cursor.execute(query, values)
                    
                    conn.commit()
                    logger.debug(f"Processed batch of {len(batch)} telemetry events")
            except Exception as e:
                logger.error(f"Error in batch processing telemetry events: {str(e)}")
                # Put events back in queue to retry
                with self.queue_lock:
                    for event in batch:
                        event['table'] = table
                        self.event_queue.append(event)
    
    def _queue_event(self, table: str, data: Dict[str, Any]):
        """Add an event to the processing queue"""
        data['table'] = table
        with self.queue_lock:
            self.event_queue.append(data)
            
            # If queue gets too large, process immediately
            if len(self.event_queue) >= self.max_queue_size:
                self._batch_processor()
    
    def record_api_request(self, 
                          endpoint: str, 
                          method: str, 
                          status_code: int, 
                          response_time_ms: float, 
                          user_agent: Optional[str] = None,
                          ip_address: Optional[str] = None,
                          request_size: Optional[int] = None,
                          response_size: Optional[int] = None,
                          error: Optional[str] = None) -> str:
        """
        Record an API request with timing and status information
        
        Returns:
            str: The request ID that can be used to link other telemetry events
        """
        request_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        data = {
            'id': request_id,
            'timestamp': timestamp,
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'user_agent': user_agent,
            'ip_address': ip_address,
            'request_size': request_size,
            'response_size': response_size,
            'error': error
        }
        
        self._queue_event('api_requests', data)
        
        # Log errors
        if status_code >= 400:
            logger.error(f"API Error: {endpoint} returned {status_code} - {error}")
        
        return request_id
    
    def record_llm_operation(self,
                            request_id: str,
                            model_id: str,
                            operation_type: str,
                            tokens_input: Optional[int] = None,
                            tokens_output: Optional[int] = None,
                            latency_ms: Optional[float] = None,
                            success: bool = True,
                            error: Optional[str] = None,
                            inference_type: Optional[str] = "aws_bedrock"):
        """
        Record an LLM operation with performance metrics
        
        Args:
            request_id: ID from record_api_request to link this operation
            model_id: The model identifier used
            operation_type: Type of operation (generate, evaluate, etc.)
            tokens_input: Number of input tokens
            tokens_output: Number of output tokens
            latency_ms: Time taken in milliseconds
            success: Whether the operation succeeded
            error: Error message if any
            inference_type: The inference type (aws_bedrock, CAII, etc.)
        """
        operation_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        data = {
            'id': operation_id,
            'request_id': request_id,
            'timestamp': timestamp,
            'model_id': model_id,
            'operation_type': operation_type,
            'tokens_input': tokens_input,
            'tokens_output': tokens_output,
            'latency_ms': latency_ms,
            'success': 1 if success else 0,
            'error': error,
            'inference_type': inference_type
        }
        
        self._queue_event('llm_operations', data)
        
        if not success:
            logger.error(f"LLM Operation Error: {model_id} - {operation_type} - {error}")
    
    def record_job_start(self,
                        request_id: str,
                        job_id: str,
                        job_type: str,
                        memory_mb: Optional[int] = None,
                        cpu_cores: Optional[int] = None,
                        input_size: Optional[int] = None) -> str:
        """
        Record the start of a CML job
        
        Returns:
            str: The job_metrics ID to use for recording job completion
        """
        metrics_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        data = {
            'id': metrics_id,
            'request_id': request_id,
            'job_id': job_id,
            'timestamp_start': timestamp,
            'timestamp_end': None,
            'job_type': job_type,
            'status': 'RUNNING',
            'memory_mb': memory_mb,
            'cpu_cores': cpu_cores,
            'input_size': input_size,
            'output_size': None,
            'error': None
        }
        
        self._queue_event('job_metrics', data)
        logger.info(f"Job started: {job_id} - {job_type}")
        
        return metrics_id
    
    def record_job_end(self,
                      metrics_id: str,
                      status: str,
                      output_size: Optional[int] = None,
                      error: Optional[str] = None):
        """
        Record the completion of a CML job
        
        Args:
            metrics_id: ID returned from record_job_start
            status: Final job status
            output_size: Size of output data
            error: Error message if job failed
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE job_metrics 
                    SET timestamp_end = ?, status = ?, output_size = ?, error = ?
                    WHERE id = ?
                    """,
                    (timestamp, status, output_size, error, metrics_id)
                )
                conn.commit()
                
                if status != 'COMPLETED':
                    logger.error(f"Job failed: {metrics_id} - {error}")
                else:
                    logger.info(f"Job completed: {metrics_id}")
        except Exception as e:
            logger.error(f"Error recording job end: {str(e)}")
    
    def record_system_metrics(self,
                             cpu_percent: float,
                             memory_percent: float,
                             disk_percent: float,
                             active_requests: int):
        """Record system resource utilization metrics"""
        metrics_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        data = {
            'id': metrics_id,
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent,
            'active_requests': active_requests
        }
        
        self._queue_event('system_metrics', data)
    
    def record_user_interaction(self,
                               session_id: str,
                               interaction_type: str,
                               details: Dict[str, Any] = None):
        """Record user interaction events for UX analysis"""
        interaction_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        data = {
            'id': interaction_id,
            'timestamp': timestamp,
            'session_id': session_id,
            'interaction_type': interaction_type,
            'details': json.dumps(details) if details else None
        }
        
        self._queue_event('user_interactions', data)
    
    def get_api_metrics(self, 
                       days: int = 7, 
                       endpoint: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get API metrics for analysis
        
        Args:
            days: Number of days to look back
            endpoint: Filter by specific endpoint
        
        Returns:
            List of metrics records
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    endpoint, 
                    COUNT(*) as request_count,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
                    MAX(timestamp) as last_request
                FROM api_requests
                WHERE timestamp >= datetime('now', ?)
                """
                
                params = [f'-{days} days']
                
                if endpoint:
                    query += " AND endpoint = ?"
                    params.append(endpoint)
                
                query += " GROUP BY endpoint ORDER BY request_count DESC"
                
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except Exception as e:
            logger.error(f"Error getting API metrics: {str(e)}")
            return []
    
    def get_model_performance(self, 
                             days: int = 7, 
                             model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get LLM model performance metrics
        
        Args:
            days: Number of days to look back
            model_id: Filter by specific model
        
        Returns:
            List of model performance records
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    model_id,
                    operation_type, 
                    COUNT(*) as operation_count,
                    AVG(latency_ms) as avg_latency,
                    AVG(tokens_input) as avg_tokens_input,
                    AVG(tokens_output) as avg_tokens_output,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as error_count
                FROM llm_operations
                WHERE timestamp >= datetime('now', ?)
                """
                
                params = [f'-{days} days']
                
                if model_id:
                    query += " AND model_id = ?"
                    params.append(model_id)
                
                query += " GROUP BY model_id, operation_type ORDER BY operation_count DESC"
                
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except Exception as e:
            logger.error(f"Error getting model performance: {str(e)}")
            return []
    
    def get_job_statistics(self, 
                          days: int = 7, 
                          job_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get job execution statistics
        
        Args:
            days: Number of days to look back
            job_type: Filter by specific job type
        
        Returns:
            List of job statistics records
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    job_type,
                    COUNT(*) as job_count,
                    AVG((julianday(timestamp_end) - julianday(timestamp_start)) * 86400000) as avg_duration_ms,
                    SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_count,
                    SUM(CASE WHEN status != 'COMPLETED' THEN 1 ELSE 0 END) as failed_count,
                    AVG(memory_mb) as avg_memory_mb,
                    AVG(cpu_cores) as avg_cpu_cores
                FROM job_metrics
                WHERE timestamp_start >= datetime('now', ?)
                    AND timestamp_end IS NOT NULL
                """
                
                params = [f'-{days} days']
                
                if job_type:
                    query += " AND job_type = ?"
                    params.append(job_type)
                
                query += " GROUP BY job_type ORDER BY job_count DESC"
                
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except Exception as e:
            logger.error(f"Error getting job statistics: {str(e)}")
            return []
    
    def get_system_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get system metrics history
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            List of system metrics records
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    timestamp,
                    cpu_percent,
                    memory_percent,
                    disk_percent,
                    active_requests
                FROM system_metrics
                WHERE timestamp >= datetime('now', ?)
                ORDER BY timestamp
                """
                
                cursor.execute(query, [f'-{hours} hours'])
                results = [dict(row) for row in cursor.fetchall()]
                return results
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return []
        
    def store_job_telemetry_id(self, job_id: str, metrics_id: str):
        """Store job telemetry metrics ID for later reference"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS job_telemetry (
                        job_id TEXT PRIMARY KEY,
                        metrics_id TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    "INSERT OR REPLACE INTO job_telemetry (job_id, metrics_id) VALUES (?, ?)",
                    (job_id, metrics_id)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing job telemetry ID: {str(e)}")

    def get_job_telemetry_id(self, job_id: str) -> str:
        """Retrieve job telemetry metrics ID"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT metrics_id FROM job_telemetry WHERE job_id = ?", (job_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error retrieving job telemetry ID: {str(e)}")
            return None


# Create a global instance of the telemetry manager
telemetry_manager = TelemetryManager()