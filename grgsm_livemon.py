#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Gr-gsm Livemon
# Author: Piotr Krysik
# Description: Interactive monitor of a single C0 channel with analysis performed by Wireshark (command to run wireshark: sudo wireshark -k -f udp -Y gsmtap -i lo)
# Generated: Tue Jan 25 18:31:12 2022
##################################################


from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import iio
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from grgsm import arfcn
from math import pi
from optparse import OptionParser
import grgsm
import pmt
import time
import sqlite3
from sqlite3 import Error

class grgsm_livemon(gr.top_block):

    def __init__(self, args="", collector='localhost', collectorport='4729', fc=941.8e6, fc_slider=939600000, gain=30, osr=4, ppm=0, samp_rate=2000000.052982, serverport='4729', shiftoff=400e3):
        gr.top_block.__init__(self, "Gr-gsm Livemon")

        ##################################################
        # Parameters
        ##################################################
        self.args = args
        self.collector = collector
        self.collectorport = collectorport
        self.fc = fc
        self.fc_slider = fc_slider
        self.gain = gain
        self.osr = osr
        self.ppm = ppm
        self.samp_rate = samp_rate
        self.serverport = serverport
        self.shiftoff = shiftoff

        ##################################################
        # Blocks
        ##################################################
        self.pluto_source_0 = iio.pluto_source('', int(fc_slider-shiftoff), int(samp_rate), int(250e3+abs(shiftoff)), 0x8000, True, True, True, "manual", 50.0, '', True)
        self.gsm_sdcch8_demapper_0 = grgsm.gsm_sdcch8_demapper(
            timeslot_nr=1,
        )
        self.gsm_receiver_0 = grgsm.receiver(osr, ([arfcn.downlink2arfcn(fc)]), ([]), False)
        self.gsm_message_printer_1 = grgsm.message_printer(pmt.intern(""), False,
            False, False)
        self.gsm_input_0 = grgsm.gsm_input(
            ppm=ppm-int(ppm),
            osr=osr,
            fc=fc_slider-shiftoff,
            samp_rate_in=samp_rate,
        )
        self.gsm_decryption_0 = grgsm.decryption(([]), 1)
        self.gsm_control_channels_decoder_0_0 = grgsm.control_channels_decoder()
        self.gsm_control_channels_decoder_0 = grgsm.control_channels_decoder()
        self.gsm_clock_offset_control_0 = grgsm.clock_offset_control(fc_slider-shiftoff, samp_rate, osr)
        self.gsm_bcch_ccch_demapper_0 = grgsm.gsm_bcch_ccch_demapper(
            timeslot_nr=0,
        )
        self.blocks_socket_pdu_0_1 = blocks.socket_pdu("UDP_CLIENT", collector, collectorport, 1500, False)
        self.blocks_socket_pdu_0_0 = blocks.socket_pdu("UDP_SERVER", '127.0.0.1', serverport, 10000, False)
        self.blocks_rotator_cc_0 = blocks.rotator_cc(-2*pi*shiftoff/samp_rate)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0_0, 'pdus'), (self.gsm_message_printer_1, 'msgs'))
        self.msg_connect((self.gsm_bcch_ccch_demapper_0, 'bursts'), (self.gsm_control_channels_decoder_0, 'bursts'))
        self.msg_connect((self.gsm_clock_offset_control_0, 'ctrl'), (self.gsm_input_0, 'ctrl_in'))
        self.msg_connect((self.gsm_control_channels_decoder_0, 'msgs'), (self.blocks_socket_pdu_0_1, 'pdus'))
        self.msg_connect((self.gsm_control_channels_decoder_0_0, 'msgs'), (self.blocks_socket_pdu_0_1, 'pdus'))
        self.msg_connect((self.gsm_decryption_0, 'bursts'), (self.gsm_control_channels_decoder_0_0, 'bursts'))
        self.msg_connect((self.gsm_receiver_0, 'C0'), (self.gsm_bcch_ccch_demapper_0, 'bursts'))
        self.msg_connect((self.gsm_receiver_0, 'measurements'), (self.gsm_clock_offset_control_0, 'measurements'))
        self.msg_connect((self.gsm_receiver_0, 'C0'), (self.gsm_sdcch8_demapper_0, 'bursts'))
        self.msg_connect((self.gsm_sdcch8_demapper_0, 'bursts'), (self.gsm_decryption_0, 'bursts'))
        self.connect((self.blocks_rotator_cc_0, 0), (self.gsm_input_0, 0))
        self.connect((self.gsm_input_0, 0), (self.gsm_receiver_0, 0))
        self.connect((self.pluto_source_0, 0), (self.blocks_rotator_cc_0, 0))

    def get_args(self):
        return self.args

    def set_args(self, args):
        self.args = args

    def get_collector(self):
        return self.collector

    def set_collector(self, collector):
        self.collector = collector

    def get_collectorport(self):
        return self.collectorport

    def set_collectorport(self, collectorport):
        self.collectorport = collectorport

    def get_fc(self):
        return self.fc

    def set_fc(self, fc):
        self.fc = fc

    def get_fc_slider(self):
        return self.fc_slider

    def set_fc_slider(self, fc_slider):
        self.fc_slider = fc_slider
        self.pluto_source_0.set_params(int(self.fc_slider-self.shiftoff), int(self.samp_rate), int(250e3+abs(self.shiftoff)), True, True, True, "manual", 50.0, '', True)
        self.gsm_input_0.set_fc(self.fc_slider-self.shiftoff)
        self.gsm_clock_offset_control_0.set_fc(self.fc_slider-self.shiftoff)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain

    def get_osr(self):
        return self.osr

    def set_osr(self, osr):
        self.osr = osr
        self.gsm_input_0.set_osr(self.osr)

    def get_ppm(self):
        return self.ppm

    def set_ppm(self, ppm):
        self.ppm = ppm
        self.gsm_input_0.set_ppm(self.ppm-int(self.ppm))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.pluto_source_0.set_params(int(self.fc_slider-self.shiftoff), int(self.samp_rate), int(250e3+abs(self.shiftoff)), True, True, True, "manual", 50.0, '', True)
        self.gsm_input_0.set_samp_rate_in(self.samp_rate)
        self.blocks_rotator_cc_0.set_phase_inc(-2*pi*self.shiftoff/self.samp_rate)

    def get_serverport(self):
        return self.serverport

    def set_serverport(self, serverport):
        self.serverport = serverport

    def get_shiftoff(self):
        return self.shiftoff

    def set_shiftoff(self, shiftoff):
        self.shiftoff = shiftoff
        self.pluto_source_0.set_params(int(self.fc_slider-self.shiftoff), int(self.samp_rate), int(250e3+abs(self.shiftoff)), True, True, True, "manual", 50.0, '', True)
        self.gsm_input_0.set_fc(self.fc_slider-self.shiftoff)
        self.gsm_clock_offset_control_0.set_fc(self.fc_slider-self.shiftoff)
        self.blocks_rotator_cc_0.set_phase_inc(-2*pi*self.shiftoff/self.samp_rate)


def argument_parser():
    description = 'Interactive monitor of a single C0 channel with analysis performed by Wireshark (command to run wireshark: sudo wireshark -k -f udp -Y gsmtap -i lo)'
    parser = OptionParser(usage="%prog: [options]", option_class=eng_option, description=description)
    parser.add_option(
        "", "--args", dest="args", type="string", default="",
        help="Set Device Arguments [default=%default]")
    parser.add_option(
        "", "--collector", dest="collector", type="string", default='localhost',
        help="Set IP or DNS name of collector point [default=%default]")
    parser.add_option(
        "", "--collectorport", dest="collectorport", type="string", default='4729',
        help="Set UDP port number of collector [default=%default]")
    parser.add_option(
        "-f", "--fc", dest="fc", type="eng_float", default=eng_notation.num_to_str(941.8e6),
        help="Set GSM channel's central frequency [default=%default]")
    parser.add_option(
        "", "--fc-slider", dest="fc_slider", type="eng_float", default=eng_notation.num_to_str(939600000),
        help="Set fc_slider [default=%default]")
    parser.add_option(
        "-g", "--gain", dest="gain", type="eng_float", default=eng_notation.num_to_str(30),
        help="Set gain [default=%default]")
    parser.add_option(
        "", "--osr", dest="osr", type="intx", default=4,
        help="Set OverSampling Ratio [default=%default]")
    parser.add_option(
        "-p", "--ppm", dest="ppm", type="eng_float", default=eng_notation.num_to_str(0),
        help="Set ppm [default=%default]")
    parser.add_option(
        "-s", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(2000000.052982),
        help="Set samp_rate [default=%default]")
    parser.add_option(
        "", "--serverport", dest="serverport", type="string", default='4729',
        help="Set UDP server listening port [default=%default]")
    parser.add_option(
        "-o", "--shiftoff", dest="shiftoff", type="eng_float", default=eng_notation.num_to_str(400e3),
        help="Set Frequency Shiftoff [default=%default]")
    return parser

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def main(top_block_cls=grgsm_livemon, options=None):
    if options is None:
        options, _ = argument_parser().parse_args()

    tb = top_block_cls(args=options.args, collector=options.collector, collectorport=options.collectorport, fc=options.fc, fc_slider=options.fc_slider, gain=options.gain, osr=options.osr, ppm=options.ppm, samp_rate=options.samp_rate, serverport=options.serverport, shiftoff=options.shiftoff)
    tb.start()

    conn = create_connection("/root/cell_info.db")
    cursor = conn.cursor()
    try:
        fc_slider = 925400000
        print(int(fc_slider))
        for i in range(int(fc_slider),960400000,200000):
            start_time = time.time()
            tb.set_fc_slider(i)
            print(tb.get_fc_slider())
            end_time = time.time()
            if conn:
                conn.execute(
                    u"INSERT INTO observations (freq) " + "VALUES (?);",
                    [str(tb.get_fc_slider())]
                )
            conn.commit()
            while(end_time - start_time <= 2):
                end_time = time.time()
        
        fc_slider = 1805000000
        print(int(fc_slider))
        for i in range(int(fc_slider),1880400000,200000):
            start_time = time.time()
            tb.set_fc_slider(i)
            print(tb.get_fc_slider())
            end_time = time.time()
            if conn:
                conn.execute(
                    u"INSERT INTO observations (freq) " + "VALUES (?);", 
                    [str(tb.get_fc_slider())]
                )
            conn.commit()
            while(end_time - start_time <= 2):
                end_time = time.time()
    
        freq_val = cursor.execute('SELECT freq FROM observations;').fetchall()
        #print(freq_val)
        for i in range(len(freq_val)):
            #print(i)
            sql_delete_query = '''DELETE from observations where cell is NULL; '''
            cursor.execute(sql_delete_query)
            conn.commit()
        print("Records deleted successfully ")
        cursor.close()
        conn.close()

        f = open("/root/.close.txt", "w+")
        f.write("1")
        f.close()

    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
