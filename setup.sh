# set environment variables
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Initialize conda
conda init

# Check if the conda environment 'pJITAI' exists
if conda info --envs | grep -q "^pJITAI"; then
  echo "Conda environment 'pJITAI' already exists. Activating the environment..."
  conda activate pJITAI
else
  echo "Conda environment 'pJITAI' does not exist. Creating the environment..."
  conda create --name pJITAI python=3.11 -y
  conda activate pJITAI
fi

# Check OS
OS_TYPE=$(uname)
if [[ "$OS_TYPE" == "Darwin" ]]; then
  echo "OS is Mac."
elif [[ "$OS_TYPE" == "Linux" ]]; then
  echo "OS is Linux."
fi

# print Python version
python --version

# update & install cron
if [[ "$OS_TYPE" == "Darwin" ]]; then
  brew update
  brew install cron
elif [[ "$OS_TYPE" == "Linux" ]]; then
  sudo apt-get update
  sudo apt-get install cron
fi

# set cron
(crontab -l 2>/dev/null; echo "* * * * * /crontab/scheduler.sh") | crontab -

# install python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# run cron
sudo service cron start

# run mysql
if [[ "$OS_TYPE" == "Darwin" ]]; then
  brew services start mysql
elif [[ "$OS_TYPE" == "Linux" ]]; then 
  sudo systemctl start mysql
fi 

MYSQL="root"
MYSQL_HOST="localhost"
MYSQL_PASSWORD="passpass"   # May need to change password from current to 'pass' manually, if this doesn't work

# Check mysql DB pJITAI exists
DB_EXISTS=$(mysql -u $MYSQL -p$MYSQL_PASSWORD -h $MYSQL_HOST -e "SHOW DATABASES LIKE 'pJITAI';" | grep "pJITAI" > /dev/null; echo "$?")

if [ $DB_EXISTS -eq 1 ]; then
  echo "Database pJITAI does not exist. Creating now..."
  mysql -u $MYSQL -p$MYSQL_PASSWORD -h $MYSQL_HOST <<EOF
  CREATE DATABASE pJITAI;
EOF
else
  echo "Database pJITAI already exists. Using the existing database."
fi

mysql -u $MYSQL -p$MYSQL_PASSWORD -h $MYSQL_HOST <<EOF
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF

echo "mysql is running, privileges flushed and db pJITAI created."

# run nginx
if [[ "$OS_TYPE" == "Darwin" ]]; then
  brew install nginx
  brew services start nginx
elif [[ "$OS_TYPE" == "Linux" ]]; then
  sudo apt-get install nginx
  sudo systemctl start nginx
fi

NGINX_PATH=$(which nginx)

# check nginx file exists
if [ -z "$NGINX_PATH" ]; then
  echo "Nginx is not installed or not found in PATH."
  exit 1
fi

mkdir -p $(dirname $(dirname $NGINX_PATH))/etc/nginx/conf.d
sudo cp -r ./nginx/* $(dirname $(dirname $NGINX_PATH))/etc/nginx/conf.d/  # copy nginx file to target folder

NGINX_FILE=$(dirname $(dirname $NGINX_PATH))/etc/nginx/nginx.conf
INCLUDE_LINE="include $(dirname $(dirname $NGINX_PATH))/etc/nginx/conf.d/*;"

if [ -f "$NGINX_FILE" ]; then
  if ! grep -qF "$INCLUDE_LINE" "$NGINX_FILE"; then
    sudo sed -i.bak "/http {/a\\
    $INCLUDE_LINE
    " "$NGINX_FILE"
    echo "Line added to $NGINX_FILE"
  else
    echo "Line alreay exists in $NGINX_FILE"
  fi
else
  echo "$NGINX_FILE does not exist."
  exit 1
fi
sudo nginx -s reload

echo "Setup has been completed!"

# gunicorn
# gunicorn --config gunicorn-cfg.py run:app
