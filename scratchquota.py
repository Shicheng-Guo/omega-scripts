#!/usr/bin/env python2.7
"""
This is to calculate disk use
"""


from subprocess import Popen, PIPE
import re
from collections import Counter
import argparse, os, time

_qfile='/share/config/quotas/lustre-scratch-user-quotas.txt'
_groupfile='/share/config/quotas/lustre-scratch-group-quotas.txt'
hep_groups = {'golling','tipton','demers','baker','baltay','hepadmin', 
              'astrousr'}

def get_group_total(group_file): 
    with open(group_file) as gfile: 
        for line in gfile: 
            fields = line.split()
            group, used, limit = fields[1:4]
            if group == 'hep': 
                return int(used), int(limit)

def get_mod_time(file_name): 
    mod_time = os.stat(file_name).st_mtime
    return time.ctime(mod_time)

def name_user(user): 
    stout, sterr = Popen(['finger',user],stdout=PIPE).communicate()
    try: 
        name = re.compile('Name: (.*) of group').search(stout).group(1)
    except AttributeError as err: 
        return 'unknown'
    return name.strip()

def get_user_use(quotas): 
    use_by_user = []
    for line in quotas: 
        try: 
            usr, group, use, limit, files, flim, mount = line.split()
            if group in hep_groups: 
                use_by_user.append( (int(use), group, usr) )
        except ValueError: 
            pass
    return sorted(use_by_user, reverse=True)

def red(st): 
    return '\033[31m' + st + '\033[m'
def yellow(st): 
    return '\033[1;33m' + st + '\033[m'
def redbold(st): 
    return '\033[1;31m' + st + '\033[m'
def green(st): 
    return '\033[1;32m' + st + '\033[m'
def blue(st): 
    return '\033[1;34m' + st + '\033[m'
def black(st): 
    return st

def prog_bar(use, total, width=80): 
    frac = float(use) / total
    color = green
    if frac > 0.95: 
        color = red
    elif frac > 0.85: 
        color = blue
    
    used_units = int(frac * width)
    bad_units = min(used_units, width)
    verybad_units = used_units - bad_units
    bads = color('='*bad_units)
    goods = green(' '*(width - bad_units))
    verybads = ''
    if verybad_units: 
        verybads = redbold('#'*verybad_units)
    fill_arr = '[' + bads + goods + verybads + ']'

    use_gb = float(use) / 1e3
    tot_gb = float(total) / 1e3
    fill_arr += ' {:.0f} of {:.0f} TB'.format(use_gb, tot_gb)
    print fill_arr
    

def get_by_user(qfile=_qfile): 
    if not os.path.isfile(qfile): 
        raise OSError("can't find " + qfile)
    hep_total = 0
    group_totals = Counter()

    print 'reading {}\n(written {})'.format(qfile, get_mod_time(qfile))
    print ''
    
    with open(qfile) as quotas: 
        use_by_user = get_user_use(quotas)

    pr_fmt = '{:<10} {:<10} {:>11} {:<30}'
    title = ('user', 'group', 'use [GB]   ', 'full name')
    empty = ('----', '-----', '-----------', '---------')
    print pr_fmt.format(*title)
    print pr_fmt.format(*empty)
    for use, group, user in use_by_user:
        if use == 0: continue
        hep_total += use
        group_totals[group] += use
    def use_str(use): 
        return '{:>5} ({:>3.0%})'.format(use, float(use) / hep_total)
    for use, group, user in use_by_user:
        if use == 0: continue
        use_pct = use_str(use)
        print pr_fmt.format(user, group, use_pct, name_user(user))
                
    print pr_fmt.format(*empty)

    grp_sort = sorted(group_totals.items(), key=lambda x: x[1], reverse=True)
    for group, total in grp_sort: 
        print pr_fmt.format('total', group, use_str(total), '')
    print pr_fmt.format(*empty)
    print pr_fmt.format('total', 'all', hep_total, '')

def get_frac_total(txtfile=_groupfile, verbose=False): 
    if not os.path.isfile(txtfile): 
        raise OSError("can't find " + txtfile)
    other_total, limit = get_group_total(txtfile)
    if verbose: 
        print ''
        print 'check from {}'.format(txtfile)
        print 'using {} of {} GB (as of {})'.format(
            other_total, limit, get_mod_time(txtfile))
    else: 
        prog_bar(other_total, limit)
        for val in xrange(100): 
            prog_bar(val, 100)

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose: 
        get_by_user()
    get_frac_total(verbose=args.verbose)
