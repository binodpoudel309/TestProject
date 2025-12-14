import dyntools as dt
from tkinter import filedialog
import os, re, math
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# 1) Load PSSE .out
# -------------------------
psseout = filedialog.askopenfilename(
    initialdir=os.getcwd(),
    defaultextension='.out',
    filetypes=[("Out File",["*.out"])],
    title="PSSE out data"
)

chanobj = dt.CHNF(psseout, outvrsn=0)
short_title, chanid, chandata = chanobj.get_data([])

# -------------------------
# 2) Build fast lookups
# -------------------------
volts, angls, plod, qlod = {}, {}, {}, {}
branchP, branchQ = {}, {}
genP, genQ = {}, {}

re_volt = re.compile(r"^VOLT\s+(\d+)\b")
re_angl = re.compile(r"^ANGL\s+(\d+)\b")
re_plod = re.compile(r"^PLOD\s+(\d+)\b")
re_qlod = re.compile(r"^QLOD\s+(\d+)\b")
re_powr_branch = re.compile(r"^POWR\s+(\d+)\s+TO\s+(\d+)\s+CKT\s+'(\d+)")
re_vars_branch = re.compile(r"^VARS\s+(\d+)\s+TO\s+(\d+)\s+CKT\s+'(\d+)")
re_powr_gen = re.compile(r"^POWR\s+(\d+)\s*\[.*?\]\s*U(\d+)\b")
re_vars_gen = re.compile(r"^VARS\s+(\d+)\s*\[.*?\]\s*U(\d+)\b")

for cid, desc in chanid.items():
    s = desc.strip()

    if m := re_volt.match(s):
        volts[int(m.group(1))] = cid
        continue
    if m := re_angl.match(s):
        angls[int(m.group(1))] = cid
        continue
    if m := re_plod.match(s):
        plod[int(m.group(1))] = cid
        continue
    if m := re_qlod.match(s):
        qlod[int(m.group(1))] = cid
        continue
    if m := re_powr_gen.match(s):
        bus, unit = int(m.group(1)), int(m.group(2))
        genP[(bus, unit)] = cid
        continue
    if m := re_vars_gen.match(s):
        bus, unit = int(m.group(1)), int(m.group(2))
        genQ[(bus, unit)] = cid
        continue
    if m := re_powr_branch.match(s):
        a, b, ck = int(m.group(1)), int(m.group(2)), int(m.group(3))
        branchP[(a, b, ck)] = cid
        continue
    if m := re_vars_branch.match(s):
        a, b, ck = int(m.group(1)), int(m.group(2)), int(m.group(3))
        branchQ[(a, b, ck)] = cid
        continue

def pick_branch(mapping, a, b, preferred_ckt=1):
    t = (a, b, preferred_ckt)
    if t in mapping:
        return mapping[t]
    options = [(ckt, cid) for (fa, tb, ckt), cid in mapping.items() if fa == a and tb == b]
    if options:
        options.sort(key=lambda x: x[0])
        return options[0][1]
    return None

# -------------------------
# 3) Inputs
# -------------------------
volt = [999, 1306]
P = [[11, 1001]]
Q = [[11, 1001]]
pload_arr = [1306]
qload_arr = [1306]
genP_arr = [[1, 1]]
genQ_arr = [[1, 1]]
preferred_ckt = 1

# -------------------------
# 4) Resolve Channels
# -------------------------
channels, titles, ylabels, types = [], [], [], []  # types tracks category

def add_channel(cid, title, ylabel, ch_type):
    if cid is not None:
        channels.append(cid)
        titles.append(title)
        ylabels.append(ylabel)
        types.append(ch_type)

for b in volt:
    cid = volts.get(b)
    add_channel(cid, f"Voltage at bus {b}", "Voltage (pu)", "volt")

for a, b in P:
    cid = pick_branch(branchP, a, b, preferred_ckt)
    add_channel(cid, f"P from {a} to {b}", "Power (MW)", "branchP")

for a, b in Q:
    cid = pick_branch(branchQ, a, b, preferred_ckt)
    add_channel(cid, f"Q from {a} to {b}", "Power (MVAr)", "branchQ")

for b in pload_arr:
    cid = plod.get(b)
    add_channel(cid, f"Power at bus {b}", "Power (MW)", "pload")

for b in qload_arr:
    cid = qlod.get(b)
    add_channel(cid, f"VAR at bus {b}", "Power (MVAr)", "qload")

for bus, unit in genP_arr:
    cid = genP.get((bus, unit))
    add_channel(cid, f"Generator P at bus {bus} U{unit}", "Power (MW)", "genP")

for bus, unit in genQ_arr:
    cid = genQ.get((bus, unit))
    add_channel(cid, f"Generator Q at bus {bus} U{unit}", "Power (MVAr)", "genQ")

if not channels:
    raise ValueError("No channels resolved.")

# -------------------------
# 5) Auto grid size
# -------------------------
n = len(channels)
rows = int(math.floor(math.sqrt(n)))
cols = int(math.ceil(n / rows))
while rows * cols < n:
    cols += 1

# -------------------------
# 6) Plot and Save
# -------------------------
x = chandata['time']
fig_name = os.path.splitext(os.path.basename(psseout))[0]
fig, ax = plt.subplots(nrows=rows, ncols=cols, figsize=(4*cols, 2.8*rows), squeeze=False, num=fig_name)

i = 0
for r in range(rows):
    for c in range(cols):
        if i >= n:
            ax[r, c].axis('off')
            continue
        ch = channels[i]
        y = np.asarray(chandata[ch])

        # Multiply loads by 100 to convert to MW/MVAr
        if types[i] in ["pload", "qload"]:
            y = y * 100.0

        ax[r, c].plot(x, y)
        ax[r, c].set_xlabel("Time (s)")
        ax[r, c].set_ylabel(ylabels[i])

        ymax = float(np.max(y))
        ymin = float(np.min(y))
        cushion = max(abs(ymax), abs(ymin)) + 0.1
        ax[r, c].set_ylim([ymin - 0.1*cushion, ymax + 0.1*cushion])

        ax[r, c].set_title(titles[i])
        i += 1

fig.tight_layout()

# Save figure as SVG
svg_path = os.path.join(os.path.dirname(psseout), f"{fig_name}.svg")
fig.savefig(svg_path, format='svg')
print(f" Figure saved as: {svg_path}")

plt.show()
