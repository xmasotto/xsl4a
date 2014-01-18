# create pipes if they don't exists
cd `dirname $0`
[ -e "sqlite_server_IN" ] || mkfifo "sqlite_server_IN"
[ -e "sqlite_server_OUT" ] || mkfifo "sqlite_server_OUT"

echo "awaiting requests:"
while sleep 0.01; do
    sqlite3 -batch <sqlite_server_IN \
	>sqlite_server_OUT 2>sqlite_server_OUT 
    echo "processed request"
done
