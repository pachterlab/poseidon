from pymata_aio.pymata3 import PyMata3

class Pymata3_board(PyMata3):

    def __init__(self):
        super().__init__(log_output=True)

        self.setup_board()

    def setup_board(self):
        #self.pump_one = self.stepper_config(6400, [2,5])
        self.stepper_config(6400, [2,5])

    def run_pump(self):
        self.stepper_step(20, 6400)

if __name__=='__main__':
    board = Pymata3_board()
    board.run_pump()
    print(board.get_pin_state(5))
    print('check')
    board.sleep(5)
