.. code:: ipython3

    import os
    import datetime
    import sys, getopt
    
    def main(argv):
        opts, args = getopt.getopt(argv, "hl:")
        for opt, arg in opts:
            if opt == '-h':
                print('-l <label>')
                sys.exit()
            elif opt in ('-l'):
                return arg
            else:
                print('Please specify label parameter first')
                sys.exit()
                
    if __name__ == '__main__':
        label = main(sys.argv[1:])
        
        try:
            while True:
                root_path = os.getcwd()
                cache_path = os.path.join(root_path, 'cache')
                movements_path = os.path.join(cache_path, 'movements')
                thresholds_path = os.path.join(movements_path, 'thresholds')
                thresholds_label_path = os.path.join(thresholds_path, label)
                os.makedirs(thresholds_label_path, exist_ok=True)
    
                # Get last threshold
                thresholds_list = os.listdir(thresholds_label_path)
                if thresholds_list == []:
                    print('Waiting for threshold data...')
                    time.sleep(10)
                    continue
                thl_float = [float(i.replace('.cache','')) for i in thresholds_list]
                thl_float.sort(reverse=True) # Descending, newest value first
                threshold_path = os.path.join(thresholds_label_path, f'{thl_float[0]}.cache')
                with open(threshold_path, 'r') as f:
                    threshold = float(f.read())
    
                readings_path = os.path.join(movements_path, 'readings')
                readings_label_path = os.path.join(readings_path, label)
                os.makedirs(readings_label_path, exist_ok=True)
    
                readings_list = os.listdir(readings_label_path)
                if readings_list == []:
                    time.sleep(0.5)
                    continue
                readings_float = [float(i.replace('.cache','')) for i in readings_list]
                readings_float.sort(reverse=False) # Ascending, oldest value first
                readings_list_ff = [str(i) + '.cache' for i in readings_float]
    
                # Store to notification channel
                notifications_path = os.path.join(cache_path, 'notifications')
                notifications_label_path = os.path.join(notifications_path, label)
                os.makedirs(notifications_label_path, exist_ok=True)
    
                for reading_fn in readings_list_ff:
                    reading_path = os.path.join(readings_label_path, reading_fn)
                    with open(reading_path, 'r') as f:
                        reading = int(f.read())
    
                    if reading > threshold:
                        notifications_path = os.path.join(notifications_label_path, reading_fn)
                        data_time = datetime.fromtimestamp(float(reading_fn.replace('.cache','')))
                        data_time = data_time.strftime('%H:%M:$S')
                        content = f'''{data_time} {label} val:{reading} threshold:{threshold}'''
                        print(content)
                        with open(notifications_path, 'w') as f:
                            f.write(content)
    
                    # Delete reading cache that has been processed
                    os.remove(reading_path)
                    
                time.sleep(0.5)
        except KeyboardInterrupt:
            print(f'Stopping movement signal server at {label}')
            pass
            

