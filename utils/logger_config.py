import logging
import os
from datetime import datetime
from pathlib import Path
from rich.logging import RichHandler


class LoggerConfig:
    """Centralized logging configuration for the mobile automation framework"""
    
    @staticmethod
    def setup_logging(test_name: str = None, log_level: str = "INFO"):
        """
        Set up logging configuration
        
        Args:
            test_name: Name of the test being executed (optional)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Generate timestamp for log file names
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create log file name
        if test_name:
            log_filename = f"{test_name}_{timestamp}.log"
        else:
            log_filename = f"mobile_automation_{timestamp}.log"
        
        log_file_path = logs_dir / log_filename
        
        # Configure logging format
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        log_format_message = '%(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Remove any existing handlers to avoid duplicate logs
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            datefmt=date_format,
            handlers=[
                # File handler - writes to log file
                logging.FileHandler(log_file_path, mode='w', encoding='utf-8'),
                # Console handler - writes to console
                 logging.StreamHandler()
                # RichHandler(rich_tracebacks=True)
            ]
        )
        
        # Set specific logger levels for external libraries to reduce noise
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('appium').setLevel(logging.INFO)
        
        # Log the setup completion
        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized. Log file: {log_file_path}")
        logger.info(f"Log level set to: {log_level.upper()}")
        
        return str(log_file_path)
    
    @staticmethod
    def get_logger(name: str):
        """
        Get a logger instance with the specified name
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(name)
    
    @staticmethod
    def setup_test_logger(test_class_name: str, test_method_name: str, log_level: str = "INFO"):
        """
        Set up logging for a specific test
        
        Args:
            test_class_name: Name of the test class
            test_method_name: Name of the test method
            log_level: Logging level
            
        Returns:
            logging.Logger: Configured logger for the test
        """
        test_name = f"{test_class_name}_{test_method_name}"
        LoggerConfig.setup_logging(test_name, log_level)
        return LoggerConfig.get_logger(test_name)
    
    @staticmethod
    def log_test_start(logger, test_method_name: str, test_id: str = None):
        """
        Log the start of a test
        
        Args:
            logger: Logger instance
            test_method_name: Name of the test method
            test_id: Optional test ID
        """
        if test_id:
            logger.info(f"=" * 80)
            logger.info(f"STARTING TEST: {test_method_name} (ID: {test_id})")
            logger.info(f"=" * 80)
        else:
            logger.info(f"=" * 80)
            logger.info(f"STARTING TEST: {test_method_name}")
            logger.info(f"=" * 80)
    
    @staticmethod
    def log_test_end(logger, test_method_name: str, duration: float, status: str = "COMPLETED"):
        """
        Log the end of a test
        
        Args:
            logger: Logger instance
            test_method_name: Name of the test method
            duration: Test duration in seconds
            status: Test status (COMPLETED, FAILED, etc.)
        """
        logger.info(f"=" * 80)
        logger.info(f"TEST {status}: {test_method_name} - Duration: {duration:.2f}s")
        logger.info(f"=" * 80)
    
    @staticmethod
    def log_step(logger, step_description: str, step_number: int = None):
        """
        Log a test step
        
        Args:
            logger: Logger instance
            step_description: Description of the step
            step_number: Optional step number
        """
        if step_number:
            logger.info(f"STEP {step_number}: {step_description}")
        else:
            logger.info(f"STEP: {step_description}")
    
    @staticmethod
    def log_assertion(logger, assertion_description: str, result: bool, expected: str = None, actual: str = None):
        """
        Log an assertion result
        
        Args:
            logger: Logger instance
            assertion_description: Description of what is being asserted
            result: Boolean result of the assertion
            expected: Expected value (optional)
            actual: Actual value (optional)
        """
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"ASSERTION: {assertion_description} - {status}")
        
        if not result and expected and actual:
            logger.error(f"  Expected: {expected}")
            logger.error(f"  Actual: {actual}")
    
    @staticmethod
    def cleanup_old_logs(days_to_keep: int = 7):
        """
        Clean up log files older than specified days
        
        Args:
            days_to_keep: Number of days to keep log files
        """
        logs_dir = Path(__file__).parent.parent / "logs"
        if not logs_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    print(f"Deleted old log file: {log_file}")
                except Exception as e:
                    print(f"Failed to delete log file {log_file}: {e}")
