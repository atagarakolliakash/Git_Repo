"""
PostgreSQL database management and random data generation
"""

import psycopg2
from psycopg2 import sql, extras
import random
import string
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Manage PostgreSQL database operations"""
    
    def __init__(self, config):
        self.config = config
        self.connection = None
    
    def connect(self) -> bool:
        """
        Connect to PostgreSQL database with retry logic
        
        Returns:
            True if connection successful, False otherwise
        """
        retries = 0
        while retries < self.config.db.max_retries:
            try:
                logger.info(f"Connecting to database at {self.config.db.host}:{self.config.db.port}...")
                
                self.connection = psycopg2.connect(
                    host=self.config.db.host,
                    port=self.config.db.port,
                    user=self.config.db.user,
                    password=self.config.db.password,
                    database=self.config.db.database,
                    connect_timeout=self.config.db.connection_timeout
                )
                
                logger.info("Successfully connected to database")
                return True
            
            except psycopg2.OperationalError as e:
                retries += 1
                logger.warning(f"Connection attempt {retries}/{self.config.db.max_retries} failed: {e}")
                
                if retries < self.config.db.max_retries:
                    import time
                    time.sleep(self.config.db.retry_delay)
            
            except Exception as e:
                logger.error(f"Unexpected error during connection: {e}")
                return False
        
        logger.error("Failed to connect to database after all retries")
        return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                self.connection = None
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """
        Execute a query
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connection:
            logger.error("Not connected to database")
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
            return False
    
    def fetch_query(self, query: str, params: tuple = None) -> List[tuple]:
        """
        Execute a SELECT query and fetch results
        
        Returns:
            List of result tuples
        """
        if not self.connection:
            logger.error("Not connected to database")
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Query fetch failed: {e}")
            return []
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    @staticmethod
    def random_email() -> str:
        """Generate random email address"""
        return f"{DatabaseManager.random_string(8)}@example.com"
    
    @staticmethod
    def random_phone() -> str:
        """Generate random phone number"""
        return f"+1{random.randint(2000000000, 9999999999)}"
    
    @staticmethod
    def random_date(days_back: int = 365) -> str:
        """Generate random date within past N days"""
        date = datetime.now() - timedelta(days=random.randint(0, days_back))
        return date.isoformat()
    
    def insert_sample_data(self, num_records: int = 10) -> bool:
        """
        Insert random sample data into tables
        
        This method detects existing tables and inserts appropriate random data.
        """
        if not self.connection:
            logger.error("Not connected to database")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Get list of tables
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                logger.warning("No tables found in database")
                cursor.close()
                return False
            
            logger.info(f"Found tables: {tables}")
            
            # Insert data based on table names
            for table in tables:
                # Get column info
                cursor.execute(f"""
                    SELECT column_name, data_type FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """, (table,))
                
                columns = cursor.fetchall()
                column_names = [col[0] for col in columns]
                column_types = {col[0]: col[1] for col in columns}
                
                if not column_names:
                    logger.warning(f"No columns found in table {table}")
                    continue
                
                logger.info(f"Inserting {num_records} records into {table}")
                
                # Generate and insert data
                for _ in range(num_records):
                    values = []
                    for col_name in column_names:
                        col_type = column_types[col_name]
                        
                        # Skip auto-increment columns
                        if 'serial' in col_type or 'identity' in col_type:
                            continue
                        
                        # Generate appropriate random data
                        if 'int' in col_type:
                            values.append(random.randint(1, 10000))
                        elif 'float' in col_type or 'numeric' in col_type or 'decimal' in col_type:
                            values.append(round(random.uniform(10, 1000), 2))
                        elif 'varchar' in col_type or 'text' in col_type or 'char' in col_type:
                            # Use context-aware random data
                            if 'email' in col_name.lower():
                                values.append(self.random_email())
                            elif 'phone' in col_name.lower():
                                values.append(self.random_phone())
                            elif 'name' in col_name.lower():
                                values.append(self.random_string(15))
                            else:
                                values.append(self.random_string())
                        elif 'date' in col_type or 'timestamp' in col_type:
                            values.append(self.random_date())
                        elif 'bool' in col_type or 'boolean' in col_type:
                            values.append(random.choice([True, False]))
                        else:
                            values.append(self.random_string())
                    
                    if values:  # Only insert if we have values
                        placeholders = ','.join(['%s'] * len(values))
                        insert_cols = ','.join(column_names[:len(values)])
                        insert_query = f"INSERT INTO {table} ({insert_cols}) VALUES ({placeholders})"
                        
                        try:
                            cursor.execute(insert_query, tuple(values))
                        except Exception as e:
                            logger.debug(f"Insert failed for {table}: {e}")
                            # Continue with next record
                            continue
                
                self.connection.commit()
                logger.info(f"Completed inserting records into {table}")
            
            cursor.close()
            logger.info("Sample data insertion completed")
            return True
        
        except Exception as e:
            logger.error(f"Error during sample data insertion: {e}")
            self.connection.rollback()
            return False
    
    def verify_data_inserted(self) -> Dict[str, int]:
        """
        Verify that data was inserted
        
        Returns:
            Dictionary of table names and record counts
        """
        if not self.connection:
            return {}
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            result = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                result[table] = count
                logger.info(f"Table '{table}' has {count} records")
            
            cursor.close()
            return result
        
        except Exception as e:
            logger.error(f"Error verifying data: {e}")
            return {}