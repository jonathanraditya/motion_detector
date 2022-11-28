from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os

hostName = '192.168.0.5'
serverPort = 5000

class MyServer(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_dir = os.getcwd()
        self.db = 'records.db'
        
        self.db_path = os.path.join(self.root_dir, self.db)

        self.in_sw = {
            'two_corner':['front_facing','side_facing','room_entry'],
            'two_entry':['left_sensor','right_sensor'],
            'one_perimeter':['carport_perimeter','large_gate','small_gate','garden_fence','garden_outer_perimeter'],
            'one_main':['parlor_window','main_door_upper','main_door_lower'],
            'one_hallway':['hallway_door','hallway_window','kitchen_lamp_switch','outdoor_lamp_switch','parlor_lamp_switch']
        }
        self.out_gb = 0
        self.out_sw = {
            'one_hallway':{
                'kitchen_lamp_switch':0,
                'outdoor_lamp_switch':0,
                'parlor_lamp_switch':0
            }
        }
        # random.seed(1209218402348023984239874891)
        # self.key = self.gethash(random.random())
        # self.key = self.gethash(self.key)
        
        self.host = '192.168.0.5'
        self.port = 5000
        
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("0,0,1", 'utf-8'))
        
        
if __name__ == '__main__':
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f'Server started http://{hostName}:{serverPort}')
    
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    webServer.server_close()
    print('Server stopped.')