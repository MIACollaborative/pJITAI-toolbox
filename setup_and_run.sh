# set environment variables
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# update & install cron (macOS)
brew update
brew install cron

# set cron
(crontab -l 2>/dev/null; echo "* * * * * /crontab/scheduler.sh") | crontab -

# install python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# run cron
sudo service cron start

# run mysql
brew services start mysql

MYSQL="root"
MYSQL_HOST="localhost"
MYSQL_PASSWORD="pass"   # May need to change password from current to 'pass' manually, if this doesn't work

mysql -u $MYSQL -p$MYSQL_PASSWORD -h $MYSQL_HOST <<EOF
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
CREATE DATABASE pjitai;
EOF

echo "mysql is running, privileges flushed and db pjitai created."

# run nginx
brew install nginx
brew services start nginx

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
  if grep -Eq "^\s*$(echo "$INCLUDE_LINE" | sed 's/[[:space:]]\+/\\s*/g')\s*$" "$NGINX_CONF_FILE"; then
    echo "Line already exists in $NGINX_FILE"
  else
    sudo sed -i.bak "/http {/a\\
    $INCLUDE_LINE
    " "$NGINX_FILE"
    echo "Line added to $NGINX_FILE"
  fi
else
  echo "$NGINX_FILE does not exist."
  exit 1
fi
sudo nginx -s reload

# gunicorn
gunicorn --config gunicorn-cfg.py run:app