#!/bin/bash
sudo fab save_all_values --hide=status,running,stdout,warnings --colorize-errors 
for f in `find . -name "*.pkt" | sort`; do
  echo "Running $f ..."
  ip tcp_metrics flush all > /dev/null 2>&1
  sudo fab configure_mptcp --hide=status,running,stdout,warnings --colorize-errors
  ../../packetdrill $f
  sudo fab restore_mptcp --hide=status,running,stdout,warnings --colorize-errors
done
#sudo fab restore_all_values --hide=status,running,stdout,warnings --colorize-errors

