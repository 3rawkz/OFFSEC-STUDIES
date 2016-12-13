""" ipcheck.py - Getting available IPs in a network.


Usage:
    ipcheck.py -h | --help
    ipcheck.py PREFIX
    ipcheck.py [(-n <pack_num> PREFIX) | (-t <timeout> PREFIX)]

Options:
   -h --help        Show the program's usage.
   -n --packnum     Number of packets to be sent.
   -t --timeout     Timeout in miliseconds for the request.
"""

import sys, os, time, threading
from threading import Thread
from threading import Event
import subprocess
import docopt


ips = [] # Global ping variable


def ping(ip, e, n=1, time_out=1000):

    global ips

    # FIX SO PLATFORM INDEPENDENT
    # Use subprocess to ping an IP
    try:
        dump_file = open('dump.txt', 'w')
        subprocess.check_call("ping -q -w%d -c%s %s" % (int(time_out), int(n), ip),
        shell=True, stdout=dump_file, stderr=dump_file)
    except subprocess.CalledProcessError as err:
        # Ip did not receive packets
        print("The IP [%s] is NOT AVAILABLE" % ip)
        return
    else:
        # Ip received packets, so available
        print("The IP [%s] is AVAILABLE" % ip)
        #ips.append(ip)
    finally:
        # File has to be closed anyway
        dump_file.close()

        # Also set the event as ping finishes
        e.set()
        ips.append(1)


def usage():
    print("Helped init")

def main(e):

    # variables needed
    timeout = 1000
    N_THREADS = 10


    # Get arguments for parsing
    arguments = docopt.docopt(__doc__)

    # Parse the arguments
    if arguments['--help'] or len(sys.argv[1:]) < 1:
        usage()
        sys.exit(0)
    elif arguments['--packnum']:
        n_packets = arguments['--packnum']
    elif arguments['--timeout']:
        timeout = arguments['--timeout']
    prefix = arguments['PREFIX']


    # Just an inner function to reuse in the main
    # loop.
    def create_thread(threads, ip, e):

        # Just code to crete a ping thread
        threads.append(Thread(target=ping, args=(ip, e)))
        threads[-1].setDaemon(True)
        threads[-1].start()
        return


    # Do the threading stuff
    threads = []

    # Loop to check all the IP's
    for i in range(1, 256):
        if len(threads) < N_THREADS:

            # Creating and starting thread
            create_thread(threads, prefix+str(i), e)

        else:
            # Wait until a thread finishes
            e.wait()

            # Get rid of finished threads
            to_del = []
            for th in threads:
                if not th.is_alive(): to_del.append(th)
            for th in to_del: threads.remove(th)

            # Cheeky clear init + create thread
            create_thread(threads, prefix+str(i), e)
            e.clear()

    time.sleep(2*timeout/1000) # Last chance to wait for unfinished pings
    print("Program ended. Number of threads active: %d." % threading.active_count())

if __name__ == "__main__":
    ev = Event()
    main(ev)