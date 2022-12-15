from global_modules import *

if __name__ == '__main__':
    vp = VibrateProcessor()
    webServer = HTTPServer((vp.host,vp.port), Vibrateserver)
    print(f'Server started http://{vp.host}:{vp.port}')
    
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    webServer.server_close()
    print('Server stopped.')