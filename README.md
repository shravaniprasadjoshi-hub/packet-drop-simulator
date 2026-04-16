# Packet Drop Simulator

## Problem Statement
Simulate packet loss using SDN flow rules. The controller selectively
drops traffic from h1 to h2, while allowing all other traffic normally.

## Topology
- 3 Hosts: h1 (10.0.0.1), h2 (10.0.0.2), h3 (10.0.0.3)
- 1 Switch: s1
- Controller: POX (OpenFlow)

## Drop Rule
- h1 --> h2 : BLOCKED
- h1 --> h3 : ALLOWED
- h3 --> h2 : ALLOWED

## Setup & Execution

### Step 1: Start POX Controller
```bash
cd ~/pox
python3 pox.py log.level --DEBUG ~/packet-drop-simulator/drop_controller.py
```

### Step 2: Start Mininet (new terminal)
```bash
cd ~/packet-drop-simulator
sudo python3 topology.py
```

### Step 3: Test

