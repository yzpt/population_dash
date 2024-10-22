python3 -m venv venv_population
source venv_population/bin/activate

pip install pandas ipykernel geopandas dash plotly nbformat openpyxl
pip install matplotlib numpy seaborn
pip install python-dotenv
pip install dash-bootstrap-components
pip freeze > app/requirements.txt

git init
git branch -M main
git add .
git commit -m "first commit"

