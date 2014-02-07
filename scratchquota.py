#!/usr/bin/env python2.7
"""
This is to calculate disk use
"""


from subprocess import Popen, PIPE
import re
from collections import Counter
import argparse

qfile='/share/config/quotas/lustre-scratch-user-quotas.txt'
groupfile='/share/config/quotas/lustre-scratch-group-quotas.txt'
hep_groups = {'golling','tipton','demers','baker','baltay','hepadmin', 
              'astrousr'}

def get_group_total(group_file): 
    with open(group_file) as gfile: 
        for line in gfile: 
            fields = line.split()
            group, used, limit = fields[1:4]
            if group == 'hep': 
                return int(used), int(limit)

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
def redbold(st): 
    return '\033[1;31m' + st + '\033[m'
def green(st): 
    return '\033[1;32m' + st + '\033[m'

def prog_bar(use, total, width=80): 
    used_units = int((float(use) / total) * 80)
    bad_units = min(used_units, width)
    bads = red('='*bad_units)
    goods = green('-'*(width - bad_units))
    fill_arr = '[' + bads + goods + ']'
    if used_units > width: 
        verybads = used_units - width
        fill_arr += red('#'*verybads)
        fill_arr += ' <-- {} GB over!'.format(use - total)
    print fill_arr
    

def get_by_user(): 
    hep_total = 0
    group_totals = Counter()
    
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

def get_frac_total(verbose=False): 
    other_total, limit = get_group_total(groupfile)
    if verbose: 
        print ''
        print 'see {} for more'.format(qfile)
        print 'cross check: using {} of {} GB (from {})'.format(
            other_total, limit, groupfile)
    else: 
        prog_bar(other_total, limit)

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose: 
        get_by_user()
    get_frac_total(args.verbose)
