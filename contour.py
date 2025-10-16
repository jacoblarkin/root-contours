#!/usr/bin/env python3

import ROOT

from array import array
import argparse

global_min = 1e6
global_min_pt = []

def get_contours(surface, level):
    global global_min, global_min_pt
    set_pt = False
    #min = 0
    min = surface.GetMinimum()
    if min < global_min: 
        global_min = min
        set_pt = True
    for i in range(surface.GetNbinsX()):
        for j in range(surface.GetNbinsY()):
            #surface.SetBinContent(i+1,j+1, surface.GetBinContent(i+1, j+1)-min)
            surface.SetBinContent(i+1,j+1, surface.GetBinContent(i+1, j+1))
            if set_pt and surface.GetBinContent(i+1, j+1) == 0:
                global_min_pt = [surface.GetXaxis().GetBinCenter(i+1), surface.GetYaxis().GetBinCenter(j+1)]
    levels = array('d', [level])
    surface.SetContour(1, levels)
    ROOT.SetOwnership(surface, 0)
    surface.Draw("cont list")
    ROOT.gPad.Update()
    contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    contours_list = []
    for c in contours:
        contour = c.First().Clone()
        ROOT.SetOwnership(contour, 0)
        contours_list.append(contour)
    return contours_list

def get_contours_surf(surface, level_surf):
    global global_min, global_min_pt
    set_pt = False
    #min = 0
    min = surface.GetMinimum()
    #level_surf.Smooth()
    if min < global_min: 
        global_min = min
        set_pt = True
    for i in range(surface.GetNbinsX()):
        for j in range(surface.GetNbinsY()):
            #surface.SetBinContent(i+1,j+1, surface.GetBinContent(i+1, j+1)-min - level_surf.GetBinContent(i+1, j+1))
            surface.SetBinContent(i+1,j+1, surface.GetBinContent(i+1, j+1) - level_surf.GetBinContent(i+1, j+1))
            if set_pt and surface.GetBinContent(i+1, j+1) == 0:
                global_min_pt = [surface.GetXaxis().GetBinCenter(i+1), surface.GetYaxis().GetBinCenter(j+1)]
    levels = array('d', [0])
    surface.SetContour(1, levels)
    ROOT.SetOwnership(surface, 0)
    surface.Draw("cont list")
    ROOT.gPad.Update()
    contours = ROOT.gROOT.GetListOfSpecials().FindObject("contours")
    contours_list = []
    for c in contours:
        contour = c.First().Clone()
        ROOT.SetOwnership(contour, 0)
        contours_list.append(contour)
    return contours_list

def get_surface(filename, surf='surf'):
    print(f'Get surface from {filename}')
    f = ROOT.TFile(filename)
    s = f.Get(surf).Clone()
    s.SetDirectory(0)
    return s

ap = argparse.ArgumentParser(prog='contour.py',description='PROfit contour plotter',epilog='Must run PROfit first!')
ap.add_argument('-o', '--outname', default='contour.pdf', type=str, help='Outputfile name')
ap.add_argument('-i', '--input', nargs='+', required=True, action='extend', help='input file list. Order must match other arguments!')
ap.add_argument('-s', '--style', nargs='+', action='extend', choices=['solid', 'dashed'], help='Plot style for each contour. Order must match other arguments!')
ap.add_argument('-c', '--color', nargs='+', action='extend', help='Color for each contour. Order must match other arguments!')
ap.add_argument('--labels', nargs='+', action='extend', help='Label for each contour in legend. Order must match other arguments!')
ap.add_argument('-p', '--point', nargs=2, help='Injected signal point if one is to be drawn')
ap.add_argument('-b', '--bestfit', action='store_true', help='Flag to draw best fit point')
ap.add_argument('-l', '--level', nargs='+', action='extend', choices=['90', '95', '99', '90_2D', '95_2D', '99_2D', '1sig', '2sig', '3sig', '4sig', '5sig', '1sig_2D', '2sig_2D', '3sig_2D', '4sig_2D', '5sig_2D', 'custom', 'fc'], help='Critical chi^2 to draw contour at assuming Wilks theorem or custom for custom chi^2 or fc for matching to a different TH2. Must have either 1 level for all or the same number and order as other per contour arguments.')
ap.add_argument('--custom', nargs='*', action='extend', type=float, help='Custom chi^2 to draw contour at if custom chose in level option. Must have either 1 or the same number as \'custom\' level.')
ap.add_argument('--fc', nargs='*', action='extend', help='Filename to get critical chi^2 surface from. Must have either 1 or the same number as \'fc\' levels.')
ap.add_argument('--fcname', default='spine_90', type=str, help='Name of TH2 in the file from fc.')
ap.add_argument('--legpos', default=[0.11, 0.11, 0.40, 0.40], type=float, nargs=4, help='Position of legend on plot in ROOT coordinates.')

args = ap.parse_args()

labels = args.labels

surfs = [get_surface(f) for f in args.input] 
minx = min(s.GetXaxis().GetXmin() for s in surfs)
miny = min(s.GetYaxis().GetXmin() for s in surfs)
maxx = max(s.GetXaxis().GetXmax() for s in surfs)
maxy = max(s.GetYaxis().GetXmax() for s in surfs)

if len(labels) < len(surfs):
    for i in range(len(surfs) - len(labels)):
        labels.append('')

cl_dict = {
    '90': 1.64,
    '90_2D': 4.61,
    '95': 2.71,
    '95_2D': 5.99,
    '99': 5.41,
    '99_2D': 9.21,
    '1sig': 0.23,
    '1sig_2D': 2.30,
    '2sig': 2.86,
    '2sig_2D': 6.18,
    '3sig': 7.74,
    '3sig_2D': 11.83,
    '4sig': 14.69,
    '4sig_2D': 19.33,
    '5sig': 23.66,
    '5sig_2D': 28.74
}

custom_counter = 0
fc_counter = 0
def cl_parse(name):
    global custom_counter
    global fc_counter
    global args
    if name == 'custom':
        if len(args.custom) == 1:
            return args.custom[0]
        else:
            custom_counter += 1
            return args.custom[custom_counter - 1]
    elif name == 'fc':
        h = get_surface(args.fc[fc_counter], args.fcname)
        fc_counter = 0 if len(args.fc) == 1 else fc_counter + 1
        return h
    return cl_dict[name]

cl = [cl_parse(args.level[0]) for i in range(len(surfs))] if len(args.level) == 1 else [cl_parse(l) for l in args.level]

if len(surfs) != len(cl):
    print("Error: expected 0, 1, or Ninput confidence levels")
    exit(1)

c = ROOT.TCanvas()
conts = [get_contours(s, l) if isinstance(l, float) else get_contours_surf(s, l) for s, l in zip(surfs, cl)]

for cl in conts:
    for c in cl:
        c.SetLineWidth(3)

style_parse = {
    'solid' : ROOT.kSolid,
    'dashed' : ROOT.kDashed
}

if len(args.style):
    if len(args.style) != len(conts):
        print(f"Error: {len(conts)} contours, but only {len(args.style)} styles provided")
        exit(1)
    for cl, s in zip(conts, args.style):
        for c in cl:
            c.SetLineStyle(style_parse[s])

color_parse = {
    'red' : ROOT.kRed,
    'blue' : ROOT.kBlue,
    'green' : ROOT.kGreen,
    'cyan' : ROOT.kCyan,
    'magenta' : ROOT.kMagenta,
    'orange' : ROOT.kOrange,
    'yellow' : ROOT.kYellow,
    'black' : ROOT.kBlack
}

if len(args.color):
    if len(args.color) != len(conts):
        print(f"Error: {len(conts)} contours, but only {len(args.color)} colors provided")
        exit(1)
    for cl, s in zip(conts, args.color):
        for c in cl:
            c.SetLineColor(color_parse[s])

c = ROOT.TCanvas()
c.cd()
c.SetLogx()
c.SetLogy()

frame = c.DrawFrame(minx, miny, maxx, maxy)
frame.GetXaxis().SetTitle(surfs[0].GetXaxis().GetTitle())
frame.GetYaxis().SetTitle(surfs[0].GetYaxis().GetTitle())
#leg = ROOT.TLegend(0.11,0.70,0.49,0.89)
leg = ROOT.TLegend(args.legpos[0], args.legpos[1], args.legpos[2], args.legpos[3])
leg.SetFillStyle(0)
leg.SetLineWidth(0)
for cl, label in zip(conts, labels): 
    leg.AddEntry(cl[0], label, "l")
    for ct in cl:
        ct.Draw("l same")
if args.point:
    p = ROOT.TGraph(1)
    p.SetPoint(0, float(args.point[0]), float(args.point[1]))
    p.SetMarkerColor(ROOT.kRed)
    p.SetMarkerStyle(ROOT.kFullCircle)
    p.Draw('p same')
    leg.AddEntry(p, 'Injected point: '+labels[len(conts)], 'p')
if args.bestfit:
    pb = ROOT.TGraph(1)
    pb.SetPoint(0, float(global_min_pt[0]), float(global_min_pt[1]))
    pb.SetMarkerColor(ROOT.kBlack)
    pb.SetMarkerStyle(ROOT.kFullCircle)
    pb.Draw('p same')
    leg.AddEntry(pb, 'Best Fit', 'p')
leg.Draw("same")
t = ROOT.TText()
t.SetNDC()
t.SetTextFont(42)
t.SetTextSize(0.03)
t.SetTextAlign(33);        
t.DrawText(0.895, 0.955, 'PROfit v1.1.6')
ROOT.gPad.Update()
c.Print(args.outname)

