import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/root/Semestre8/Minichallenge/Puzzlebot-Papuland/install/puzzlebot_sim'
