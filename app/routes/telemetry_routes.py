from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any, List
from app.core.telemetry import telemetry_manager

router = APIRouter(prefix="/telemetry", tags=["telemetry"])



@router.get("/api-metrics")
async def get_api_metrics(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    endpoint: Optional[str] = Query(None, description="Filter by specific endpoint")
) -> Dict[str, Any]:
    metrics = telemetry_manager.get_api_metrics(days=days, endpoint=endpoint)
    total_requests = sum(m.get('request_count', 0) for m in metrics)
    total_errors = sum(m.get('error_count', 0) for m in metrics)
    avg_response_time = (sum(m.get('avg_response_time', 0) * m.get('request_count', 0) for m in metrics)
                         / total_requests if total_requests > 0 else 0)
    # Aggregate counts for the new bar chart
    generation = sum(m.get('request_count', 0) for m in metrics 
                     if '/synthesis/generate' in m.get('endpoint', '') or '/synthesis/freeform' in m.get('endpoint', ''))
    evaluation = sum(m.get('request_count', 0) for m in metrics 
                     if '/synthesis/evaluate' in m.get('endpoint', '') or '/synthesis/evaluate_freeform' in m.get('endpoint', ''))
    export_requests = sum(m.get('request_count', 0) for m in metrics 
                          if '/export' in m.get('endpoint', ''))
    request_groups = [
       {"name": "Generation", "requests": generation},
       {"name": "Evaluation", "requests": evaluation},
       {"name": "Export", "requests": export_requests}
    ]
    return {
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate": total_errors / total_requests if total_requests > 0 else 0,
        "avg_response_time": avg_response_time,
        "endpoints": metrics,
        "request_groups": request_groups
    }


@router.get("/model-performance")
async def get_model_performance(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    model_id: Optional[str] = Query(None, description="Filter by specific model")
) -> Dict[str, Any]:
    """
    Get LLM model performance metrics
    
    Returns:
        Dict with model performance statistics
    """
    metrics = telemetry_manager.get_model_performance(days=days, model_id=model_id)
    
    # Group by inference type
    inference_types = {}
    for m in metrics:
        infer_type = m.get('inference_type', 'unknown')
        if infer_type not in inference_types:
            inference_types[infer_type] = []
        inference_types[infer_type].append(m)
    
    return {
        "models_count": len(set(m.get('model_id', '') for m in metrics)),
        "total_operations": sum(m.get('operation_count', 0) for m in metrics),
        "avg_latency": sum(m.get('avg_latency', 0) * m.get('operation_count', 0) 
                          for m in metrics) / sum(m.get('operation_count', 0) 
                                                for m in metrics) if metrics else 0,
        "by_inference_type": inference_types,
        "models": metrics
    }

@router.get("/job-statistics")
async def get_job_statistics(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    job_type: Optional[str] = Query(None, description="Filter by specific job type")
) -> Dict[str, Any]:
    """
    Get CML job execution statistics
    
    Returns:
        Dict with job execution statistics
    """
    metrics = telemetry_manager.get_job_statistics(days=days, job_type=job_type)
    
    total_jobs = sum(m.get('job_count', 0) for m in metrics)
    completed_jobs = sum(m.get('completed_count', 0) for m in metrics)
    failed_jobs = sum(m.get('failed_count', 0) for m in metrics)
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0,
        "avg_duration_ms": sum(m.get('avg_duration_ms', 0) * m.get('job_count', 0) 
                              for m in metrics) / total_jobs if total_jobs > 0 else 0,
        "by_job_type": metrics
    }

@router.get("/system-metrics")
async def get_system_metrics(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back")
) -> Dict[str, Any]:
    """
    Get system resource utilization metrics
    
    Returns:
        Dict with system metrics history
    """
    metrics = telemetry_manager.get_system_metrics_history(hours=hours)
    
    # Calculate current averages
    current_metrics = metrics[-10:] if len(metrics) >= 10 else metrics
    
    avg_cpu = sum(m.get('cpu_percent', 0) for m in current_metrics) / len(current_metrics) if current_metrics else 0
    avg_memory = sum(m.get('memory_percent', 0) for m in current_metrics) / len(current_metrics) if current_metrics else 0
    avg_disk = sum(m.get('disk_percent', 0) for m in current_metrics) / len(current_metrics) if current_metrics else 0
    avg_requests = sum(m.get('active_requests', 0) for m in current_metrics) / len(current_metrics) if current_metrics else 0
    
    # Find peak values
    peak_cpu = max((m.get('cpu_percent', 0) for m in metrics), default=0)
    peak_memory = max((m.get('memory_percent', 0) for m in metrics), default=0)
    peak_requests = max((m.get('active_requests', 0) for m in metrics), default=0)
    
    return {
        "current": {
            "cpu_percent": avg_cpu,
            "memory_percent": avg_memory,
            "disk_percent": avg_disk,
            "active_requests": avg_requests
        },
        "peak": {
            "cpu_percent": peak_cpu,
            "memory_percent": peak_memory,
            "active_requests": peak_requests
        },
        "history": metrics
    }

@router.get("/export-data")
async def export_telemetry_data(
    data_type: str = Query(..., description="Type of data to export: 'api', 'model', 'job', 'system', 'all'"),
    days: int = Query(30, ge=1, le=365, description="Number of days of data to export"),
    format: str = Query("json", description="Export format: 'json' or 'csv'")
) -> Dict[str, Any]:
    """
    Export raw telemetry data for analysis or backup
    
    Args:
        data_type: Type of telemetry data to export
        days: Number of days of data to export
        format: Export format (currently only JSON supported)
        
    Returns:
        Dict with requested telemetry data
    """
    result = {}
    
    try:
        with telemetry_manager._get_db_connection() as conn:
            cursor = conn.cursor()
            
            if data_type in ["api", "all"]:
                cursor.execute(
                    "SELECT * FROM api_requests WHERE timestamp >= datetime('now', ?) ORDER BY timestamp DESC",
                    [f'-{days} days']
                )
                result["api_requests"] = [dict(row) for row in cursor.fetchall()]
            
            if data_type in ["model", "all"]:
                cursor.execute(
                    "SELECT * FROM llm_operations WHERE timestamp >= datetime('now', ?) ORDER BY timestamp DESC",
                    [f'-{days} days']
                )
                result["llm_operations"] = [dict(row) for row in cursor.fetchall()]
            
            if data_type in ["job", "all"]:
                cursor.execute(
                    "SELECT * FROM job_metrics WHERE timestamp_start >= datetime('now', ?) ORDER BY timestamp_start DESC",
                    [f'-{days} days']
                )
                result["job_metrics"] = [dict(row) for row in cursor.fetchall()]
            
            if data_type in ["system", "all"]:
                cursor.execute(
                    "SELECT * FROM system_metrics WHERE timestamp >= datetime('now', ?) ORDER BY timestamp DESC",
                    [f'-{days} days']
                )
                result["system_metrics"] = [dict(row) for row in cursor.fetchall()]
                
            if data_type not in ["api", "model", "job", "system", "all"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid data_type: {data_type}. Must be one of: 'api', 'model', 'job', 'system', 'all'"
                )
        
        # If CSV format is requested, convert to CSV (implementation would be here)
        if format == "csv":
            # This would normally convert the data to CSV and return as a file
            # For now, just note that we would do this
            return {"message": "CSV export not yet implemented, returning JSON", "data": result}
            
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting telemetry data: {str(e)}"
        )

@router.get("/dashboard")
async def get_telemetry_dashboard() -> Dict[str, Any]:
    """
    Get a comprehensive dashboard with key telemetry metrics
    
    Returns:
        Dict with overview of all telemetry metrics
    """
    # Get recent data for all metrics
    api_metrics = telemetry_manager.get_api_metrics(days=1)
    model_metrics = telemetry_manager.get_model_performance(days=1)
    job_metrics = telemetry_manager.get_job_statistics(days=1)
    system_metrics = telemetry_manager.get_system_metrics_history(hours=24)
    
    # Calculate high-level metrics
    total_requests_24h = sum(m.get('request_count', 0) for m in api_metrics)
    error_rate_24h = sum(m.get('error_count', 0) for m in api_metrics) / total_requests_24h if total_requests_24h > 0 else 0
    
    # Get top endpoints by usage
    top_endpoints = sorted(api_metrics, key=lambda x: x.get('request_count', 0), reverse=True)[:5]
    
    # Get top models by usage
    top_models = sorted(model_metrics, key=lambda x: x.get('operation_count', 0), reverse=True)[:5]
    
    # Calculate system resource averages
    recent_system = system_metrics[-10:] if len(system_metrics) >= 10 else system_metrics
    avg_cpu = sum(m.get('cpu_percent', 0) for m in recent_system) / len(recent_system) if recent_system else 0
    avg_memory = sum(m.get('memory_percent', 0) for m in recent_system) / len(recent_system) if recent_system else 0
    
    return {
        "summary": {
            "total_requests_24h": total_requests_24h,
            "error_rate_24h": error_rate_24h,
            "avg_cpu_24h": avg_cpu,
            "avg_memory_24h": avg_memory,
            "job_success_rate": sum(m.get('completed_count', 0) for m in job_metrics) / 
                               sum(m.get('job_count', 0) for m in job_metrics) 
                               if sum(m.get('job_count', 0) for m in job_metrics) > 0 else 0
        },
        "top_endpoints": top_endpoints,
        "top_models": top_models,
        "system_load": {
            "timestamps": [m.get('timestamp') for m in system_metrics[-24:] if 'timestamp' in m],
            "cpu": [m.get('cpu_percent', 0) for m in system_metrics[-24:] if 'cpu_percent' in m],
            "memory": [m.get('memory_percent', 0) for m in system_metrics[-24:] if 'memory_percent' in m]
        }
    }