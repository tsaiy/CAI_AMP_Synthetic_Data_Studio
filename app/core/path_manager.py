from pathlib import Path
import os
from typing import Union, List
from contextlib import contextmanager

class PathManager:
    """
    Centralized path management system for handling paths in both composable and non-composable environments
    """
    def __init__(self):
        val = os.getenv("IS_COMPOSABLE", "false")
        self.is_composable = val.lower() in ('true', '1', 'yes', 'on', 't')
        self.base_dir = "synthetic-data-studio" if self.is_composable else ""
        self._setup_common_paths()

    def _setup_common_paths(self):
        """Initialize commonly used paths"""
        self.root_dir = Path(self.base_dir) if self.base_dir else Path()
        self.app_dir = self.root_dir / "app"
        self.build_dir = self.root_dir / "build"
        self.client_dir = self.root_dir / "client"
        self.upload_dir = self.root_dir / "document_upload"

    def get_path(self, *paths: str) -> Path:
        """
        Get a path that's properly prefixed based on environment
        
        Args:
            *paths: Path components to join
            
        Returns:
            Path object with proper prefix
        """
        return self.root_dir.joinpath(*paths)

    def get_str_path(self, *paths: str) -> str:
        """
        Get a string path that's properly prefixed based on environment
        
        Args:
            *paths: Path components to join
            
        Returns:
            String path with proper prefix
        """
        return str(self.get_path(*paths))

    def get_relative_path(self, path: Union[str, Path], from_path: Union[str, Path] = None) -> str:
        """
        Get a relative path that works in both environments
        
        Args:
            path: Path to convert to relative
            from_path: Optional path to make relative to (defaults to current directory)
            
        Returns:
            Relative path as string
        """
        full_path = self.get_path(str(path))
        if from_path:
            from_full_path = self.get_path(str(from_path))
            return str(Path(full_path).relative_to(from_full_path))
        return str(Path(full_path).relative_to(os.getcwd()))

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if a path exists in the appropriate environment"""
        return self.get_path(str(path)).exists()

    def make_dirs(self, path: Union[str, Path], exist_ok: bool = True) -> None:
        """Create directories ensuring proper path prefix"""
        self.get_path(str(path)).mkdir(parents=True, exist_ok=exist_ok)

    @contextmanager
    def in_project_directory(self):
        """Context manager for temporarily changing to the project directory"""
        original_dir = os.getcwd()
        try:
            if self.is_composable:
                os.chdir(self.base_dir)
            yield
        finally:
            os.chdir(original_dir)

    def get_file_size(self, paths: List[Union[str, Path]]) -> int:
        """
        Calculate total size of files in bytes
        
        Args:
            paths: List of paths to calculate size for
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        for path in paths:
            file_path = self.get_path(str(path))
            if file_path.exists():
                total_size += file_path.stat().st_size
        return total_size


