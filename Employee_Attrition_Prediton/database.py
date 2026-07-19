import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime
import os

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                database='employee_attrition',
                user='root',
                password=''
            )
            if self.conn.is_connected():
                print("Connected to MySQL database")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.conn = None
            return False
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if self.conn is None or not self.conn.is_connected():
                self.connect()
            
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.conn.commit()
                cursor.close()
                return True
        except Error as e:
            print(f"Query error: {e}")
            return None
    
    def import_csv_to_database(self, csv_file_path='employee_attrition.csv'):
        """Import employee data from CSV file to MySQL database"""
        try:
            if not os.path.exists(csv_file_path):
                print(f"ERROR: CSV file not found at {csv_file_path}")
                return False
            
            # Read CSV with tab separator
            print(f"Reading CSV file: {csv_file_path}")
            df = pd.read_csv(csv_file_path, sep='\t')
            print(f"Successfully read {len(df)} records from CSV")
            
            if self.conn is None or not self.conn.is_connected():
                self.connect()
            
            cursor = self.conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM employees")
            self.conn.commit()
            print("Cleared existing employee data")
            
            # Insert each row
            inserted_count = 0
            error_count = 0
            batch_size = 100
            batch = []
            
            query = """
            INSERT INTO employees (
                employee_number, age, daily_rate, department, distance_from_home,
                education, education_field, environment_satisfaction, hourly_rate,
                job_involvement, job_level, job_role, job_satisfaction,
                marital_status, monthly_income, monthly_rate, num_companies_worked,
                percent_salary_hike, performance_rating, relationship_satisfaction,
                stock_option_level, total_working_years, training_times_last_year,
                work_life_balance, years_at_company, years_in_current_role,
                years_since_last_promotion, years_with_curr_manager,
                overtime, gender, business_travel, attrition
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
            """
            
            def clean_value(val):
                if pd.isna(val):
                    return None
                return val
            
            for index, row in df.iterrows():
                try:
                    params = (
                        clean_value(row.get('EmployeeNumber')),
                        clean_value(row.get('Age')),
                        clean_value(row.get('DailyRate')),
                        clean_value(row.get('Department')),
                        clean_value(row.get('DistanceFromHome')),
                        clean_value(row.get('Education')),
                        clean_value(row.get('EducationField')),
                        clean_value(row.get('EnvironmentSatisfaction')),
                        clean_value(row.get('HourlyRate')),
                        clean_value(row.get('JobInvolvement')),
                        clean_value(row.get('JobLevel')),
                        clean_value(row.get('JobRole')),
                        clean_value(row.get('JobSatisfaction')),
                        clean_value(row.get('MaritalStatus')),
                        clean_value(row.get('MonthlyIncome')),
                        clean_value(row.get('MonthlyRate')),
                        clean_value(row.get('NumCompaniesWorked')),
                        clean_value(row.get('PercentSalaryHike')),
                        clean_value(row.get('PerformanceRating')),
                        clean_value(row.get('RelationshipSatisfaction')),
                        clean_value(row.get('StockOptionLevel')),
                        clean_value(row.get('TotalWorkingYears')),
                        clean_value(row.get('TrainingTimesLastYear')),
                        clean_value(row.get('WorkLifeBalance')),
                        clean_value(row.get('YearsAtCompany')),
                        clean_value(row.get('YearsInCurrentRole')),
                        clean_value(row.get('YearsSinceLastPromotion')),
                        clean_value(row.get('YearsWithCurrManager')),
                        clean_value(row.get('OverTime')),
                        clean_value(row.get('Gender')),
                        clean_value(row.get('BusinessTravel')),
                        clean_value(row.get('Attrition'))
                    )
                    
                    batch.append(params)
                    
                    if len(batch) >= batch_size:
                        cursor.executemany(query, batch)
                        self.conn.commit()
                        inserted_count += len(batch)
                        print(f"  Inserted {inserted_count} records...")
                        batch = []
                        
                except Exception as e:
                    error_count += 1
                    print(f"Error at row {index}: {e}")
                    continue
            
            if batch:
                cursor.executemany(query, batch)
                self.conn.commit()
                inserted_count += len(batch)
            
            cursor.close()
            
            print(f"\n========== IMPORT COMPLETE ==========")
            print(f"Successfully inserted: {inserted_count} employees")
            print(f"Errors encountered: {error_count}")
            print(f"=====================================\n")
            
            return self.verify_import()
            
        except Exception as e:
            print(f"ERROR during import: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_import(self):
        """Verify the import by counting records"""
        try:
            if self.conn is None or not self.conn.is_connected():
                self.connect()
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees")
            count = cursor.fetchone()[0]
            cursor.close()
            
            print(f"VERIFICATION: {count} records now in employees table")
            
            if count > 0:
                cursor = self.conn.cursor()
                cursor.execute("SELECT employee_number, age, department, attrition FROM employees LIMIT 3")
                samples = cursor.fetchall()
                print("Sample records:")
                for sample in samples:
                    print(f"  Employee #{sample[0]}, Age: {sample[1]}, Dept: {sample[2]}, Attrition: {sample[3]}")
                cursor.close()
            
            return count > 0
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    def insert_employee(self, employee_data):
        """Insert employee data"""
        query = """
        INSERT INTO employees (
            employee_number, age, daily_rate, department, distance_from_home,
            education, education_field, environment_satisfaction, hourly_rate,
            job_involvement, job_level, job_role, job_satisfaction,
            marital_status, monthly_income, monthly_rate, num_companies_worked,
            percent_salary_hike, performance_rating, relationship_satisfaction,
            stock_option_level, total_working_years, training_times_last_year,
            work_life_balance, years_at_company, years_in_current_role,
            years_since_last_promotion, years_with_curr_manager,
            overtime, gender, business_travel, attrition
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            age = VALUES(age), daily_rate = VALUES(daily_rate),
            department = VALUES(department), distance_from_home = VALUES(distance_from_home),
            education = VALUES(education), education_field = VALUES(education_field),
            environment_satisfaction = VALUES(environment_satisfaction),
            hourly_rate = VALUES(hourly_rate),
            job_involvement = VALUES(job_involvement), job_level = VALUES(job_level),
            job_role = VALUES(job_role), job_satisfaction = VALUES(job_satisfaction),
            marital_status = VALUES(marital_status), monthly_income = VALUES(monthly_income),
            monthly_rate = VALUES(monthly_rate),
            num_companies_worked = VALUES(num_companies_worked),
            percent_salary_hike = VALUES(percent_salary_hike),
            performance_rating = VALUES(performance_rating),
            relationship_satisfaction = VALUES(relationship_satisfaction),
            stock_option_level = VALUES(stock_option_level),
            total_working_years = VALUES(total_working_years),
            training_times_last_year = VALUES(training_times_last_year),
            work_life_balance = VALUES(work_life_balance),
            years_at_company = VALUES(years_at_company),
            years_in_current_role = VALUES(years_in_current_role),
            years_since_last_promotion = VALUES(years_since_last_promotion),
            years_with_curr_manager = VALUES(years_with_curr_manager),
            overtime = VALUES(overtime), gender = VALUES(gender),
            business_travel = VALUES(business_travel), attrition = VALUES(attrition)
        """
        
        def clean_value(val):
            if pd.isna(val):
                return None
            return val
        
        params = (
            clean_value(employee_data.get('EmployeeNumber')),
            clean_value(employee_data.get('Age')),
            clean_value(employee_data.get('DailyRate')),
            clean_value(employee_data.get('Department')),
            clean_value(employee_data.get('DistanceFromHome')),
            clean_value(employee_data.get('Education')),
            clean_value(employee_data.get('EducationField')),
            clean_value(employee_data.get('EnvironmentSatisfaction')),
            clean_value(employee_data.get('HourlyRate')),
            clean_value(employee_data.get('JobInvolvement')),
            clean_value(employee_data.get('JobLevel')),
            clean_value(employee_data.get('JobRole')),
            clean_value(employee_data.get('JobSatisfaction')),
            clean_value(employee_data.get('MaritalStatus')),
            clean_value(employee_data.get('MonthlyIncome')),
            clean_value(employee_data.get('MonthlyRate')),
            clean_value(employee_data.get('NumCompaniesWorked')),
            clean_value(employee_data.get('PercentSalaryHike')),
            clean_value(employee_data.get('PerformanceRating')),
            clean_value(employee_data.get('RelationshipSatisfaction')),
            clean_value(employee_data.get('StockOptionLevel')),
            clean_value(employee_data.get('TotalWorkingYears')),
            clean_value(employee_data.get('TrainingTimesLastYear')),
            clean_value(employee_data.get('WorkLifeBalance')),
            clean_value(employee_data.get('YearsAtCompany')),
            clean_value(employee_data.get('YearsInCurrentRole')),
            clean_value(employee_data.get('YearsSinceLastPromotion')),
            clean_value(employee_data.get('YearsWithCurrManager')),
            clean_value(employee_data.get('OverTime')),
            clean_value(employee_data.get('Gender')),
            clean_value(employee_data.get('BusinessTravel')),
            clean_value(employee_data.get('Attrition'))
        )
        
        return self.execute_query(query, params)
    
    def save_prediction(self, employee_number, prediction):
        """Save a prediction result"""
        query = """
        INSERT INTO predictions (
            employee_number, actual_attrition, predicted_attrition,
            risk_score, risk_tier
        ) VALUES (%s, %s, %s, %s, %s)
        """
        
        params = (
            employee_number,
            prediction.get('Actual_Attrition'),
            prediction.get('Predicted_Attrition'),
            prediction.get('Attrition_Risk_Score'),
            prediction.get('Risk_Tier')
        )
        
        return self.execute_query(query, params)
    
    def save_feature_importance(self, features, model_name):
        """Save feature importance scores"""
        query = """
        INSERT INTO feature_importance (feature_name, importance, model_name)
        VALUES (%s, %s, %s)
        """
        
        for feature, importance in features.items():
            params = (feature, importance, model_name)
            self.execute_query(query, params)
        
        return True
    
    def save_model_metrics(self, model_name, metrics):
        """Save model performance metrics"""
        query = """
        INSERT INTO model_metrics (
            model_name, accuracy, precision_score, recall, f1_score, roc_auc
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        params = (
            model_name,
            metrics.get('Accuracy', 0),
            metrics.get('Precision', 0),
            metrics.get('Recall', 0),
            metrics.get('F1-Score', 0),
            metrics.get('ROC-AUC', 0)
        )
        
        return self.execute_query(query, params)
    
    def get_employees(self, limit=100):
        """Get all employees"""
        query = f"SELECT * FROM employees LIMIT {limit}"
        return self.execute_query(query)
    
    def get_predictions(self, limit=100):
        """Get all predictions"""
        query = f"SELECT * FROM predictions ORDER BY prediction_date DESC LIMIT {limit}"
        return self.execute_query(query)
    
    def get_high_risk_employees(self, threshold=0.66):
        """Get high risk employees"""
        query = f"""
        SELECT e.*, p.risk_score, p.risk_tier, p.predicted_attrition
        FROM employees e
        JOIN predictions p ON e.employee_number = p.employee_number
        WHERE p.risk_score >= {threshold}
        ORDER BY p.risk_score DESC
        """
        return self.execute_query(query)
    
    def close(self):
        """Close database connection"""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("MySQL connection closed")


# For testing the database connection
if __name__ == "__main__":
    db = Database()
    if db.conn:
        print("✅ Database connection successful!")
        
        # Check if data exists
        result = db.execute_query("SELECT COUNT(*) as count FROM employees")
        if result:
            print(f"📊 Total employees in database: {result[0]['count']}")
    else:
        print("❌ Database connection failed!")
    db.close()
    