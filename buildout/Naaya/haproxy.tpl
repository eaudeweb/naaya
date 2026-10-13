global
    maxconn     4000

defaults
    mode                    http
    #option http-server-close
    option forwardfor       except 127.0.0.0/8
    option                  redispatch
    retries                 3
    timeout http-request    10s
    timeout queue           1m
    timeout connect         10s
    timeout client          15m
    timeout server          15m
    #timeout http-keep-alive 10s
    timeout check           10s
    maxconn                 3000

frontend main
    bind                        ${frontend-bind}
    default_backend             ${frontend-backend}

${backends}
