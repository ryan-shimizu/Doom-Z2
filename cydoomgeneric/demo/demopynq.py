import sys
from typing import Optional

import numpy as np
import pygame
import socket
import time
import cydoomgeneric as cdg
import multiprocessing
from multiprocessing.managers import SharedMemoryManager
from multiprocessing import shared_memory

SELF_ADDR = '192.168.0.101'
SELF_PORT = 65432
BUF_SIZE = 1024

# define bitmasks
L_STICK_UP    = 10
L_STICK_DOWN  = 9
L_STICK_LEFT  = 8
L_STICK_RIGHT = 7
L_STICK_USE   = 6
R_STICK_L     = 5
R_STICK_R     = 4
R_STICK_ESC   = 3
BTN_FIRE      = 2
BTN_RUN       = 1
BTN_ENTER     = 0

keymap = {
    L_STICK_LEFT: cdg.Keys.LEFTARROW,
    L_STICK_RIGHT: cdg.Keys.RIGHTARROW,
    L_STICK_UP: cdg.Keys.UPARROW,
    L_STICK_DOWN: cdg.Keys.DOWNARROW,
    R_STICK_L: cdg.Keys.STRAFE_L,
    R_STICK_R: cdg.Keys.STRAFE_R,
    BTN_FIRE: cdg.Keys.FIRE,
    L_STICK_USE: cdg.Keys.USE,
    BTN_RUN: cdg.Keys.RSHIFT,
    BTN_ENTER: cdg.Keys.ENTER,
    R_STICK_ESC: cdg.Keys.ESCAPE,
}

class PygameDoom:    
    def __init__(self) -> None:
        self._resx = 320
        self._resy = 200
        self.frame_idx = 0
        self.control_frame_cache = b'\x00\x00'
        self.control_frame_shared = shared_memory.ShareableList([0,],name="control_frame")
        self.sock_l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_l.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_l.bind((SELF_ADDR, SELF_PORT))
        self.sock_l.listen()
        print('SERVER: Waiting for connection from client...')
        self.conn, self.addr = self.sock_l.accept()
        print('SERVER: Connected to client.')
        self.p1 = multiprocessing.Process(target=self.run_server, name="server")
        self.p1.start()
        pygame.init()
        self._screen = pygame.display.set_mode((self._resx, self._resy))

    def run_server(self):
        while True:
            fetched_control_frame = shared_memory.ShareableList(sequence=None, name="control_frame")
            data = self.conn.recv(BUF_SIZE)
            binary_representation = ' '.join(format(byte, '08b') for byte in data)
            binary_representation_cache = fetched_control_frame[0]
            print(f"SERVER: Received messsage {binary_representation} from client, was {hex(binary_representation_cache)}.")
            fetched_control_frame[0] = int.from_bytes(data, byteorder='big',signed=False)
            time.sleep(0.02)

    def get_keyval(self,idx):
        return (self.control_frame_shared[0] >> idx) & 0x1

    def draw_frame(self, pixels: np.ndarray) -> None:
        pixels = np.rot90(pixels)
        pixels = np.flipud(pixels)
        pygame.surfarray.blit_array(self._screen, pixels[:, :, [2, 1, 0]])
        pygame.display.flip()

    def get_key(self) -> Optional[tuple[int, int]]:
        if(self.frame_idx == 11):
            self.frame_idx = 0
            return None
        else:
            bit_idx = self.frame_idx
            self.frame_idx += 1
            get_keyval_result = self.get_keyval(bit_idx)
            keymap_result = keymap[bit_idx]
            return get_keyval_result, keymap_result

    def set_window_title(self, t: str) -> None:
        pygame.display.set_caption(t)

if __name__ == "__main__":
    g = PygameDoom()
    cdg.init(g._resx,
             g._resy,
             g.draw_frame,
             g.get_key,
             set_window_title=g.set_window_title)
    cdg.main()
