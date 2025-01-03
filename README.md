# Bench Test Automation Suite

## Table of Contents

1. Overview
2. Setting Up a New Workstation
   - Clone the Repository
   - Set Up Python Environment
   - Run the Setup Script
3. Adding Experimental Custom Methods
   - Where to Add Custom Methods
   - Writing a Custom Method
   - Testing the Experimental Method
4. Promoting a Proven Experimental Method
5. Workflow for Method Development
   - Git Workflow
   - Key Points for Clean Workflow
6. Example Workflow
7. Troubleshooting
8. Contact

---

## 1. Overview

The Bench Test Automation Suite is a modular Python framework for automating tests with dynamic method integration. It allows users to add and test new methods easily while maintaining a clean and organized structure. This README provides setup instructions, development guidelines, and workflow practices.

---

## 2. Setting Up a New Workstation

### Clone the Repository

Run the following commands to clone the repository and navigate to the project directory:

git clone <repository_url>
cd Bench_Test_Automation_Suite

### Set Up Python Environment

1. Install Python 3.7+ if not already installed.
2. Create and activate a virtual environment:

python3 -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows

3. Install required dependencies:

pip install -r requirements.txt

### Run the Setup Script

Run the provided setup script to configure your environment:

python setup_project.py

This script will:

- Automatically add the project root to PYTHONPATH.
- Update your shell configuration (e.g., ~/.bashrc or ~/.zshrc).

Note: Restart your terminal or run source ~/.bashrc (or equivalent) to apply the changes.

---

## 3. Adding Experimental Custom Methods

### Where to Add Custom Methods

Add experimental methods to the following folder:

Bench_Test_Automation_Suite/B1500_SMU/Methods/Custom_Methods/

- Each method must be in its own file.
- The file name must match the method name.

### Writing a Custom Method

Create a new file in the Custom_Methods folder. For example:

Bench_Test_Automation_Suite/B1500_SMU/Methods/Custom_Methods/example_method.py

Define the method inside the file:

def example_method(self, param1, param2):
    return f"Processing {param1} and {param2} in example_method."

### Testing the Experimental Method

Write a test script in the Scripts/ folder to test your method:

from B1500_SMU.B1500_SMU_Core import B1500_SMU

b1500 = B1500_SMU()
print(b1500.example_method("data1", "data2"))

Run the script:

python Scripts/example_usage.py

---

## 4. Promoting a Proven Experimental Method

1. Move the tested and proven file from Custom_Methods/ to the main Methods/ folder:

Bench_Test_Automation_Suite/B1500_SMU/Methods/example_method.py

2. Ensure the file name matches the method name for consistency.
3. Commit and push the changes to GitHub for review.

---

## 5. Workflow for Method Development

### Git Workflow

1. Create a New Branch

Start a new branch for each method:

git checkout -b feature/<method_name>

Example:

git checkout -b feature/example_method

2. Work on the Method

Write your method in the appropriate folder and test it using a script.

3. Commit Changes

Save progress frequently:

git add .
git commit -m "Added example_method for testing"

4. Push the Branch

Push your branch to GitHub:

git push origin feature/<method_name>

5. Open a Pull Request

Once the method is complete and tested, open a pull request for review and merging.

### Key Points for Clean Workflow

- One File Per Method: This makes methods easier to search and manage.
- File Name Matches Method Name: Ensures clarity and consistency.
- Frequent Commits: Avoid losing progress due to errors by committing regularly.
- Branch Isolation: Work on one branch per method to avoid conflicts.
- Move Proven Methods: Promote tested methods to the main Methods folder.

---

## 6. Example Workflow

1. Create a new branch:

git checkout -b feature/example_method

2. Write the method in Custom_Methods/example_method.py:

def example_method(self, param1, param2):
    return f"Processing {param1} and {param2} in example_method."

3. Test the method using a script:

from B1500_SMU.B1500_SMU_Core import B1500_SMU

b1500 = B1500_SMU()
print(b1500.example_method("data1", "data2"))

4. Move the file to Methods/ after testing and push to GitHub:

mv B1500_SMU/Methods/Custom_Methods/example_method.py B1500_SMU/Methods/
git add .
git commit -m "Promoted example_method to Methods"
git push origin feature/example_method

---

## 7. Troubleshooting

### ModuleNotFoundError

- Ensure the setup_project.py script was run successfully.
- Verify that PYTHONPATH includes the project root:

echo $PYTHONPATH

### Git Conflicts

- Always pull the latest changes before starting new work:

git checkout main
git pull origin main
git checkout -b feature/<method_name>

---

## 8. Contact

For issues or questions, please reach out to the project maintainer or open an issue on GitHub.

Happy coding! 🚀
