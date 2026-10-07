"""Run the fixed-feature comparison through the existing matched trainer."""
import argparse
import transition245 as trainer

CONTROL=trainer.OUT/'DTM063/protocol.json'
OUT=trainer.h.ROOT/'reports/work/TRANSITION-246/artifacts'


def run():
    trainer.OUT=OUT
    trainer.run(experiments=[('DTM065',False)],linear_only=True,matched_control=CONTROL)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
