"""
Run this script to import employee data from CSV to MySQL database
"""
from database import Database
import os

def main():
    print("=" * 60)
    print("EMPLOYEE DATA IMPORT TOOL")
    print("=" * 60)
    
    # Check if CSV exists
    csv_file = 'employee_attrition.csv'
    if not os.path.exists(csv_file):
        print(f"\nERROR: Cannot find '{csv_file}'")
        print("Please make sure the CSV file is in the current directory")
        print(f"Current directory: {os.getcwd()}")
        
        # Try to find CSV in common locations
        possible_paths = [
            'employee_attrition.csv',
            '../employee_attrition.csv',
            './employee_attrition.csv',
            'data/employee_attrition.csv',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found CSV at: {path}")
                csv_file = path
                break
        else:
            return
    
    # Connect to database
    print("\nConnecting to database...")
    db = Database()
    
    # Check if connection was successful
    if db.conn is None:
        print("ERROR: Failed to connect to database")
        print("Make sure XAMPP MySQL is running")
        print("\nTroubleshooting steps:")
        print("1. Open XAMPP Control Panel")
        print("2. Click 'Start' next to MySQL")
        print("3. Wait for MySQL to start (should turn green)")
        print("4. Run this script again")
        return
    
    # Import data
    print("\nStarting import...")
    success = db.import_csv_to_database(csv_file)
    
    if success:
        print("\n✅ DATA IMPORT SUCCESSFUL!")
        print("The dashboard will now show employee data")
    else:
        print("\n❌ DATA IMPORT FAILED")
        print("Check the error messages above")
    
    # Close connection
    db.close()

if __name__ == "__main__":
    main()
    