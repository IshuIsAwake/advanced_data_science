# builds docs/ads_assignment_report.pdf , the plain english report for both parts
# run it after the notebooks , the charts read what they write to data/
import glob
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image , KeepTogether , PageBreak , Paragraph , SimpleDocTemplate , Spacer , Table , TableStyle

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)
from self_module import diff_in_means

data = os.path.join(root , 'data')
figures = os.path.join(data , 'report')
os.makedirs(figures , exist_ok=True)

# carlito looks like calibri , dejavu is the fallback , both have the rupee sign
carlito = glob.glob('/var/lib/flatpak/runtime/*/x86_64/*/active/files/share/fonts/google-crosextra-carlito/')
if carlito:
    faces = {k : carlito[0] + f'Carlito-{v}.ttf' for k , v in [('Body' , 'Regular') , ('Body-Bold' , 'Bold') , ('Body-Italic' , 'Italic') , ('Body-BoldItalic' , 'BoldItalic')]}
else:
    d = '/usr/share/fonts/truetype/dejavu/DejaVuSans'
    faces = {'Body' : d + '.ttf' , 'Body-Bold' : d + '-Bold.ttf' , 'Body-Italic' : d + '-Oblique.ttf' , 'Body-BoldItalic' : d + '-BoldOblique.ttf'}
for name , path in faces.items():
    pdfmetrics.registerFont(TTFont(name , path))
    font_manager.fontManager.addfont(path)
pdfmetrics.registerFontFamily('Body' , normal='Body' , bold='Body-Bold' , italic='Body-Italic' , boldItalic='Body-BoldItalic')

series , series2 = '#2a78d6' , '#eb6834'
ink , ink2 , muted , grid , axis = '#0b0b0b' , '#52514e' , '#898781' , '#e1e0d9' , '#c3c2b7'
plt.rcParams.update({'font.family' : font_manager.FontProperties(fname=faces['Body']).get_name() , 'font.size' : 8.5 , 'text.color' : ink ,
                     'axes.edgecolor' : axis , 'axes.linewidth' : 0.6 , 'xtick.color' : ink2 , 'ytick.color' : ink2 ,
                     'xtick.major.size' : 0 , 'ytick.major.size' : 0 , 'axes.titlesize' : 9.5 , 'axes.titleweight' : 'bold' , 'axes.titlelocation' : 'left'})


def clean(ax , along='y'):
    ax.spines[['top' , 'right']].set_visible(False)
    ax.grid(axis=along , color=grid , linewidth=0.5)
    ax.set_axisbelow(True)


def heading(fig , title , note=None):
    fig.text(0.01 , 0.945 , title , fontsize=9.5 , fontweight='bold' , color=ink , va='center')
    if note:
        fig.text(0.01 , 0.885 , note , fontsize=7.8 , color=ink2 , va='center')


def save(fig , name):
    path = os.path.join(figures , name)
    fig.savefig(path , dpi=300 , facecolor='white')
    plt.close(fig)
    return path


# ---------- part 1 charts ----------

train = pd.read_parquet(os.path.join(data , 'ctr' , 'train_sample.parquet') , columns=['click' , 'hour' , 'site_id' , 'banner_pos' , 'device_type' , 'device_conn_type'])
overall = train['click'].mean() * 100


def placement_chart():
    # these columns are stored as text
    web = train['site_id'] != '85f751fd'
    code = lambda c , t : train[c].astype(str) == str(t)
    groups = [[('Website' , web) , ('App' , ~web)] ,
              [(f'Position {t}' , code('banner_pos' , t)) for t in [1 , 0]] ,
              [(f'Connection type {t}' , code('device_conn_type' , t)) for t in [0 , 2 , 3]] ,
              [(f'Device type {t}' , code('device_type' , t)) for t in [0 , 1 , 4]]]
    labels , rates , at , y = [] , [] , [] , 0
    for g in groups:
        for name , mask in g:
            assert mask.any() , name
            labels.append(f'{name} ({mask.mean() * 100:.0f}%)')
            rates.append(train.loc[mask , 'click'].mean() * 100)
            at.append(y)
            y += 1
        y += 0.6
    fig , ax = plt.subplots(figsize=(3.45 , 2.25))
    fig.subplots_adjust(left=0.36 , right=0.97 , top=0.82 , bottom=0.155)
    ax.barh(at , rates , color=series , height=0.62)
    for a , r in zip(at , rates):
        ax.text(r + 0.4 , a , f'{r:.1f}%' , va='center' , fontsize=7.5 , color=ink , zorder=4 , bbox=dict(facecolor='white' , edgecolor='none' , pad=0.5))
    ax.axvline(overall , color=muted , linewidth=0.9)
    ax.set_yticks(at , labels , fontsize=7.8)
    ax.invert_yaxis()
    ax.set_xlim(0 , 26)
    ax.set_xlabel('CTR (%)' , color=ink2 , labelpad=2)
    heading(fig , 'Some placements get far more clicks' , f'In brackets: share of all ads. Grey line: all ads, {overall:.1f}%')
    clean(ax , 'x')
    return save(fig , 'placement.png')


def hour_chart():
    hour = train['hour'].astype(str).str[-2:].astype(int)
    rate = train.groupby(hour)['click'].mean() * 100
    fig , ax = plt.subplots(figsize=(3.45 , 2.25))
    fig.subplots_adjust(left=0.11 , right=0.97 , top=0.82 , bottom=0.155)
    ax.plot(rate.index , rate.values , color=series , linewidth=1.6)
    for h , place in [(rate.idxmax() , 1.3) , (rate.idxmin() , -2.6)]:
        ax.plot(h , rate[h] , 'o' , color=series , markersize=4)
        ax.text(h , rate[h] + place , f'{rate[h]:.1f}% at {h:02d}:00' , fontsize=7.5 , color=ink)
    ax.set_ylim(0 , 25)
    ax.set_xlim(0 , 23)
    ax.set_xticks(range(0 , 24 , 4))
    ax.set_xlabel('Hour of the day' , color=ink2 , labelpad=2)
    ax.set_ylabel('CTR (%)' , color=ink2 , labelpad=2)
    heading(fig , 'The hour barely changes the CTR' , 'It stays between 16% and 19% all day')
    clean(ax)
    return save(fig , 'hour.png')


def model_chart():
    test = pd.read_parquet(os.path.join(data , 'ctr' , 'logistic_test.parquet') , columns=['p'])['p'].values
    y = pd.read_parquet(os.path.join(data , 'ctr' , 'y_test.parquet')).values.ravel()
    bins = pd.qcut(test , 10 , labels=False)
    actual = pd.Series(y).groupby(bins).mean().values * 100
    said = pd.Series(test).groupby(bins).mean().values * 100
    x = np.arange(1 , 11)
    fig , ax = plt.subplots(figsize=(6.85 , 2.05))
    fig.subplots_adjust(left=0.065 , right=0.99 , top=0.865 , bottom=0.265)
    ax.bar(x , actual , color=series , width=0.62 , label='Actual CTR')
    ax.plot(x , said , 'o' , color=series2 , markersize=5 , markeredgecolor='white' , markeredgewidth=0.8 , label='Predicted CTR')
    ax.text(x[0] , actual[0] + 2.2 , f'{actual[0]:.1f}%' , fontsize=8 , color=ink , ha='center')
    ax.text(x[-1] + 0.36 , actual[-1] - 2.5 , f'{actual[-1]:.1f}%' , fontsize=8 , color=ink)
    ax.set_xticks(x , ['1\nleast confident'] + [str(i) for i in x[1:-1]] + ['10\nmost confident'])
    ax.set_xlim(0.4 , 11)
    ax.set_ylim(0 , 47)
    ax.set_ylabel('CTR (%)' , color=ink2 , labelpad=2)
    ax.set_xlabel('Bins of test ads, sorted by predicted CTR' , color=ink2 , labelpad=2)
    heading(fig , 'Where the model predicts a higher CTR, the actual CTR is higher')
    ax.legend(frameon=False , loc='upper left' , fontsize=8)
    clean(ax)
    return save(fig , 'model.png')


# ---------- part 2 charts ----------

jobs = pd.read_csv(os.path.join(data , 'jtpa_india_synthetic_40000.csv'))


def group_chart(outcome , scale , label , title , name):
    rows = [(f'Everyone ({len(jobs):,})' , diff_in_means(jobs[outcome].values , jobs['assigned_to_training'].values))]
    for g in ['General' , 'OBC' , 'SC' , 'ST']:
        d = jobs[jobs['social_category'] == g]
        rows.append((f'{g} ({len(d):,})' , diff_in_means(d[outcome].values , d['assigned_to_training'].values)))
    fig , ax = plt.subplots(figsize=(3.45 , 1.7))
    fig.subplots_adjust(left=0.25 , right=0.98 , top=0.86 , bottom=0.13)
    top = max(r['ci high'] for _ , r in rows) * scale
    for i , (_ , r) in enumerate(rows):
        c , lo , hi = r['diff'] * scale , r['ci low'] * scale , r['ci high'] * scale
        ax.plot([lo , hi] , [i , i] , color=series , linewidth=1.5 , solid_capstyle='butt')
        ax.plot(c , i , 'o' , color=series , markersize=5 , markeredgecolor='white' , markeredgewidth=0.8)
        ax.text(hi + top * 0.04 , i , label(c) , va='center' , fontsize=7.8 , color=ink)
    ax.axvline(0 , color=muted , linewidth=0.9)
    ax.set_yticks(range(len(rows)) , [n for n , _ in rows] , fontsize=7.8)
    ax.invert_yaxis()
    ax.set_xlim(left=-top * 0.03 , right=top * 1.32)
    ax.xaxis.set_major_formatter(lambda v , _ : f'{v:,.0f}')
    heading(fig , title)
    clean(ax , 'x')
    return save(fig , name)


# ---------- the document ----------

base = dict(fontName='Body' , textColor=colors.black)
styles = {
    'title' : ParagraphStyle('title' , **base , fontSize=15.5 , leading=19 , alignment=TA_CENTER , spaceAfter=8 , fontNameBold='Body-Bold') ,
    'part' : ParagraphStyle('part' , **base , fontSize=14 , leading=17 , spaceBefore=4 , spaceAfter=5 , keepWithNext=1) ,
    'section' : ParagraphStyle('section' , **base , fontSize=11.5 , leading=14 , spaceBefore=6 , spaceAfter=2.5 , keepWithNext=1) ,
    'body' : ParagraphStyle('body' , **base , fontSize=10.3 , leading=12.8 , spaceAfter=4) ,
    'bullet' : ParagraphStyle('bullet' , **base , fontSize=10.3 , leading=12.8 , spaceAfter=2 , leftIndent=14 , bulletIndent=3 , bulletFontName='Body' , bulletFontSize=10.3) ,
    'cell' : ParagraphStyle('cell' , **base , fontSize=9.4 , leading=11.3) ,
    'center' : ParagraphStyle('center' , **base , fontSize=9.4 , leading=11.3 , alignment=TA_CENTER) ,
}
width = A4[0] - 2 * 1.7 * cm


def P(text , style='body'):
    return Paragraph(text , styles[style])


def B(text):
    return Paragraph(text , styles['bullet'] , bulletText='•')


def N(i , text):
    return Paragraph(text , styles['bullet'] , bulletText=f'{i}.')


def part(text):
    return P(f'<b>{text}</b>' , 'part')


def section(text):
    return P(f'<b>{text}</b>' , 'section')


def table(rows , widths , center_from=None):
    cells = []
    for i , row in enumerate(rows):
        line = []
        for j , c in enumerate(row):
            style = 'center' if center_from is not None and j >= center_from else 'cell'
            line.append(P(f'<b>{c}</b>' if i == 0 else c , style))
        cells.append(line)
    t = Table(cells , colWidths=[w * width for w in widths])
    t.setStyle(TableStyle([('GRID' , (0 , 0) , (-1 , -1) , 0.5 , colors.black) , ('BACKGROUND' , (0 , 0) , (-1 , 0) , colors.HexColor('#efefef')) ,
                           ('VALIGN' , (0 , 0) , (-1 , -1) , 'MIDDLE') , ('TOPPADDING' , (0 , 0) , (-1 , -1) , 2.2) , ('BOTTOMPADDING' , (0 , 0) , (-1 , -1) , 3) ,
                           ('LEFTPADDING' , (0 , 0) , (-1 , -1) , 4) , ('RIGHTPADDING' , (0 , 0) , (-1 , -1) , 4)]))
    return t


def picture(path , w):
    from PIL import Image as Pil
    a , b = Pil.open(path).size
    return Image(path , width=w , height=w * b / a)


def pair(a , b):
    t = Table([[picture(a , width * 0.485) , picture(b , width * 0.485)]] , colWidths=[width * 0.5] * 2)
    t.setStyle(TableStyle([('VALIGN' , (0 , 0) , (-1 , -1) , 'TOP') , ('LEFTPADDING' , (0 , 0) , (-1 , -1) , 0) , ('RIGHTPADDING' , (0 , 0) , (-1 , -1) , 0) ,
                           ('TOPPADDING' , (0 , 0) , (-1 , -1) , 2) , ('BOTTOMPADDING' , (0 , 0) , (-1 , -1) , 2)]))
    return t


repo = 'https://github.com/IshuIsAwake/advanced_data_science'
kaggle = 'https://www.kaggle.com/c/avazu-ctr-prediction'

s = []
s.append(P('<b>ADS Assignment Report - Ishan Batra - CSE 3 - 240485</b>' , 'title'))
s.append(P(f'This report is only a summary of what was done and what was found. All the code and detailed results are at: <a href="{repo}" color="blue">{repo}</a>'))

# ---------- part 1 ----------

s.append(P(f'<b>Part 1: Avazu Click Rate Prediction:</b> <font size="10.3"><a href="{kaggle}" color="blue">{kaggle}</a></font>' , 'part'))

s.append(section('1. Business Understanding'))
s.append(P('An ad platform shows ads on websites and inside apps. We assume it gets paid when an ad is clicked, so it wants to know which ads are likely to be clicked and put its budget there.'))
s.append(P('<b>What we predict:</b> the column <i>click</i>, which is 1 if an ad was clicked and 0 if not. The share of ads that get clicked is the <b>click-through rate (CTR)</b>.'))
s.append(P('<b>Questions we asked:</b> What share of ads get clicked? Which devices, apps, websites, positions and hours get more clicks? Can a model predict clicks better than a simple guess? Where should the budget go?'))

s.append(section('2. Dataset Summary and EDA'))
s.append(P("<b>The data:</b> click logs from Avazu's Kaggle competition: 40.4 million ads shown over 10 days in October 2014, already split into training (80%), validation (10%) and test (10%) rows. The dfSummary overview is in the notebook <i>01_eda</i>."))
s.append(P("<b>Our sample:</b> every 40th row of each split, about 1 million rows, because that is what fits in our graphics card's memory. All 40 million rows come later, with batching (training in small chunks) and a neural network written from scratch. The sample still looks like the full data: the quietest hour has 11,877 rows in full and 298 in the sample, the busiest has 358,731 and 8,967, and hourly CTRs differ only as much as chance would."))
s.append(table([['Columns' , 'What they hold' , 'Why they matter'] ,
                ['click' , 'Clicked or not (1 or 0)' , 'This is what we predict'] ,
                ['hour' , 'Date and hour, stored as a number' , 'People may click more at some times'] ,
                ['banner_pos' , 'Position of the ad, as a code' , 'Some positions get more attention'] ,
                ['site_id, site_domain, site_category' , 'Which website, as scrambled text codes' , 'Some websites get far more clicks'] ,
                ['app_id, app_domain, app_category' , 'Which app, as scrambled text codes' , 'Some apps get far more clicks'] ,
                ['device_id, device_ip, device_model, device_type, device_conn_type' , 'Which device, its model and type, and its connection, as codes' , 'They go along with clicks. The ID and IP point to individual people'] ,
                ['C1, C14 to C21' , 'Hidden columns, their meaning is not disclosed' , 'They still help predict clicks']] , [0.36 , 0.33 , 0.31]))
s.append(Spacer(1 , 5))
s.append(B('<b>Size:</b> 24 columns, all of them categories, even the ones that look like numbers.'))
s.append(B('<b>Missing values:</b> no blank cells, but some values stand in for "unknown". One device ID sits on 82.5% of rows, with 377,512 different IP addresses, which no single device could have. App ads carry filler values in the website columns and the reverse, so we read website categories on website ads only and app categories on app ads only. This is our reading of the patterns, since the data has no definitions.'))
s.append(B('<b>Clicks and no clicks:</b> 17% clicked and 83% did not. A model that always says "no click" would be 83% correct and still useless, so we do not judge models by accuracy.'))
s.append(pair(placement_chart() , hour_chart()))
s.append(B('Website ads get a higher CTR than app ads: 19.8% against 12.0%.'))
s.append(B('Position 1 gets 18.4%, position 0 16.5%. Connection matters more: type 0 gets 18.1%, types 3 and 5 under 5%.'))
s.append(B('Device type 0 gets 20.9%, type 1 (92% of ads) 16.9%, types 4 and 5 about 9.5%. These codes are not defined.'))
s.append(B('Within websites, the 8 largest categories run from 28.3% to 3.3%. Within apps, they run from 25.0% to 9.0%.'))
s.append(B('The hour barely matters for CTR, even though traffic varies from 2% to 6% of ads from hour to hour.'))

s.append(section('3. Machine Learning'))
s.append(P('<b>Preparing the data:</b>'))
s.append(B('Split <i>hour</i> into hour of the day and day of the week.'))
s.append(B('Removed the row number, and the device ID and IP address, because they identify individual people.'))
s.append(B('Removed columns that add little, and measured what each one cost in log loss (explained below, lower is better). Removing C14 saved 421 columns and raised log loss by 0.0009. Removing C18, C19 and C21 saved 108 columns and raised it by 0.0001. Removing app_domain saved 24 and raised it by 0.0001. Removing C1 saved 5 and barely changed it. With all of them kept, the model does not fit in memory.'))
s.append(B('Grouped values under 0.025% of training rows into "other", and turned categories into 1,356 yes or no columns.'))
s.append(B('The test rows played no part in any of this, so nothing leaked from them into the model.'))
s.append(Spacer(1 , 3))
s.append(table([['Model' , 'In simple words' , 'Log loss' , 'ROC-AUC' , 'PR-AUC' , 'F1'] ,
                ['Baseline' , 'Gives every ad the same predicted CTR, explained below.' , '0.458' , '0.500' , '0.171' , '0'] ,
                ['<b>Logistic regression</b>' , 'Gives each column a weight, adds them up and turns the total into a predicted CTR.' , '<b>0.405</b>' , '<b>0.734</b>' , '<b>0.358</b>' , '<b>0.408</b>'] ,
                ['Weighted logistic regression' , 'The same, but clicks count about 5 times as much in training, so the rare clicks are not ignored.' , '0.603' , '0.734' , '0.357' , '0.407'] ,
                ['Weighted linear SVM' , 'Looks for a line that separates clicks from no clicks. It gives a score, not a predicted CTR, so it has no log loss.' , '-' , '0.717' , '0.312' , '0.396']] ,
               [0.2 , 0.48 , 0.08 , 0.09 , 0.08 , 0.07] , center_from=2))
s.append(Spacer(1 , 4))
s.append(B('<b>Log loss:</b> how close the predicted CTRs were to what happened. Lower is better.'))
s.append(B('<b>ROC-AUC:</b> take one clicked ad and one unclicked ad. This is how often the model gives the clicked one the higher score. 0.5 is guessing and 1 is perfect.'))
s.append(B('<b>PR-AUC:</b> how many of the ads with the highest scores were really clicked. Guessing scores about 0.17.'))
s.append(B('<b>F1:</b> for a yes or no call, the balance between catching clicks and avoiding false alarms. We set the cut-off on the validation rows by best F1, because the cut-off with the best accuracy, near 0.5, catches only 7% of clicks.'))
s.append(P('Scores are on 101,073 test rows. <b>Plain logistic regression is the best model:</b> its log loss is 11.5% lower than the baseline and it ranks ads better than the SVM. We wrote the models from scratch in PyTorch. Logistic regression matches the standard library (sklearn) to 3 decimals, and the SVM comes close (ROC-AUC 0.717 against 0.713).'))
s.append(P('<b>The baseline</b> gives every ad the average CTR of the training rows, 17%, and uses nothing about the ad. We picked it because it is the simplest possible model, and no other fixed number gets a lower log loss on the training rows, so beating it means a model learned from the columns. It cannot rank ads (ROC-AUC 0.5) and never says "click" (F1 0).'))

s.append(KeepTogether([section('4. Inference and Interpretation') ,
                     P("<b>How this graph is made:</b> we took the raw output of logistic regression, its predicted CTR, for every ad in the test set, sorted the ads by it and split them into 10 equal bins. Bin 1 holds the ads where the model is least confident of a click, and bin 10 the ads where it is most confident. For each bin we compare the average predicted CTR with the actual CTR.") ,
                     picture(model_chart() , width)]))
s.append(B('<b>Ranking:</b> where the model is less confident, the actual CTR is lower, and where it is more confident, the actual CTR is higher. Bin 1 gets 1.8% and bin 10 gets 41.1%, a 23 times gap.'))
s.append(B('<b>Predicted against actual:</b> the two are close in every bin. In bin 10 the model predicts 42.7% and the actual CTR is 41.1%. The other nine bins are within about 1 point.'))
s.append(B('<b>Overfitting:</b> log loss is 0.402 on the training rows and 0.405 on the test rows, so the model is not just memorising the training rows.'))
s.append(B('<b>Weighted model:</b> it ranks ads just as well (ROC-AUC 0.734), but its predicted CTRs are far too high: 44% on average against an actual 17%.'))
s.append(B('<b>Most useful columns:</b> app, C17 (a hidden column), device model and website raise log loss the most when removed.'))
s.append(B('<b>Prediction is not cause.</b> The model shows what goes along with clicks. Position 1 gets a higher CTR, but better ads may simply be given position 1. Only an experiment that places ads at random (an A/B test) can show whether moving an ad changes its CTR.'))
s.append(B('<b>Limits:</b> one row in 40 used; rare values grouped; hidden and scrambled columns that are hard to explain; only 10 days, with test rows from the same days, so new days will probably score a bit worse; a simple model that misses combinations (this app on this device); no history per user; no prices.'))

s.append(section('5. Recommendations'))
s.append(N(1 , '<b>Rank ads by predicted CTR × price per click.</b> Run each ad through plain logistic regression to get a predicted CTR, multiply it by the price per click (what the client pays us for the ad), then sort. The ads with the highest predicted CTR × price per click should get the most budget. The price is not in our data, so it has to come from the platform.'))
s.append(N(2 , '<b>Put the budget on the highest predicted CTRs.</b> The 30% of ads with the highest predicted CTR got an actual CTR of about 32%, and the lowest 30% about 4.5%.'))
s.append(N(3 , '<b>Test before shifting budget.</b> Website ads, connection type 0 and device type 0 have higher CTRs than the rest. Connection types 3 and 5, device types 4 and 5, and the weakest website categories (f66779e6 and 76b2941d, under 4%) are the first places to cut. These are patterns and may not be causes, so try them on a small share of the budget in an A/B test.'))
s.append(N(4 , "<b>Do not use the weighted model's predicted CTR,</b> because it is far too high."))
s.append(N(5 , '<b>Next steps:</b> train on all 40 million rows, add a neural network that can learn combinations, add history per user, and check the model on the last day of data.'))

# ---------- part 2 ----------

s.append(PageBreak())
s.append(part('Part 2: Evaluating a Job Training Programme'))
s.append(P('<b>Important:</b> this data is synthetic, made for practice. It is not evidence about any real Indian government programme.'))

s.append(section('Business Understanding'))
s.append(P('The government ran a lottery and offered subsidised job training to the winners. Those offered could enrol or decline, and a few not offered enrolled anyway. Employment and earnings were recorded at 18 and 30 months. The government asks: what does offering training do, what does the training itself do, and do OBC, SC and ST applicants benefit? We used the linked file: 40,000 applicants in 45 districts (the assignment says 10,000 in 16).'))

s.append(section('1. Data Understanding and Randomisation'))
s.append(B('<b>The data:</b> 40,000 applicants and 25 columns. The only blanks are in training type, exactly for the 23,140 people who did not enrol, so they mean "no training".'))
s.append(B('<b>Was the lottery fair?</b> If it was, those offered and not offered should differ only by chance. We compared them on 14 background facts (past earnings, schooling, age, caste and so on). The largest gap is the SC share (18.3% against 17.4%, or 0.025 standard deviations), and it is also the only p value below 0.05 (p = 0.017). At a 5% false positive rate, 14 tests are expected to give 14 × 0.05 = 0.7 false positives, so one is not surprising. With the Bonferroni correction the cut-off becomes 0.05 / 14 = 0.00357, and 0.017 is clearly above it. In every state, exactly 2 in 3 applicants were offered training. The lottery looks fair.'))
s.append(Spacer(1 , 2))
s.append(table([['' , 'Did not enrol' , 'Enrolled' , 'Total' , 'Enrolment rate'] ,
                ['Not offered' , '12,927' , '406' , '13,333' , '3.0%'] ,
                ['Offered' , '10,213' , '16,454' , '26,667' , '61.7%']] , [0.28 , 0.18 , 0.18 , 0.18 , 0.18] , center_from=1))
s.append(Spacer(1 , 4))
s.append(B('<b>First stage:</b> the offer raised enrolment by 58.7 points (95% confidence interval 58.0 to 59.3).'))
s.append(B('<b>Noncompliance:</b> 38% of those offered never enrolled, and 406 people enrolled without an offer. So being offered and being trained are not the same. Comparing people who enrolled with people who did not would mix the effect of training with the kind of person who chooses to enrol.'))

s.append(section('2. Intent-to-Treat (ITT) Analysis'))
s.append(P('<b>Every number in this section compares everyone offered training with everyone not offered.</b> Someone offered counts as offered even if they never enrolled, and someone not offered counts as not offered even if they enrolled anyway. The lottery made the two groups alike, so the difference is caused by the offer. These numbers are the effect of being offered training. The effect on the people who actually took it is section 3.'))
s.append(table([['Outcome' , 'Offered' , 'Not offered' , 'Difference in means' , '95% confidence interval'] ,
                ['Employed at 18 months' , '46.2%' , '43.1%' , '+3.1 points' , '2.1 to 4.1'] ,
                ['Employed at 30 months' , '46.9%' , '43.0%' , '+4.0 points' , '2.9 to 5.0'] ,
                ['Earnings at 18 months' , '₹58,712' , '₹52,161' , '+₹6,551' , '₹5,036 to ₹8,067'] ,
                ['Earnings at 30 months' , '₹76,406' , '₹67,329' , '+₹9,076' , '₹7,084 to ₹11,069']] , [0.26 , 0.14 , 0.14 , 0.2 , 0.26] , center_from=1))
s.append(Spacer(1 , 4))
s.append(B("<b>How we test it:</b> we want to see whether zero, meaning no effect, lies outside the 95% confidence interval (CI) of the difference in means. The CI is the difference ± 1.96 standard errors, from Welch's t-test, which does not assume both groups vary equally (its standard errors are heteroskedasticity-robust). The standard error says how much the difference would move by chance from one sample to the next. 1.96 is the 95% value of the t distribution, which is effectively normal with this many people. If we repeated the study 100 times, about 95 of the CIs would contain the true effect."))
s.append(B('<b>Result:</b> zero lies far outside all four CIs (every p is below 0.001), so the offer raises both employment and earnings.'))
s.append(B('<b>For policymakers:</b> on average, an applicant offered training earns about ₹9,000 more at 30 months, 13.5% above those not offered, and employment is 4.0 points higher. This counts the 38% who never took the training.'))
s.append(B("<b>Does the effect grow over time?</b> The earnings effect rises by ₹2,525 from 18 to 30 months (95% CI ₹212 to ₹4,838), though as a share of the not offered group's earnings it barely moves (12.6% to 13.5%). The employment effect rises by 0.84 points, which could be chance (p = 0.24)."))
s.append(B("<b>Not done yet:</b> repeating this with baseline covariates (each person's background), as the assignment asks."))

s.append(section('3. Instrumental Variables and LATE'))
s.append(P("<b>Not done yet.</b> This step would estimate the effect of the training itself on the people who actually took it, using the Wald estimator and two-stage least squares, and cover monotonicity, the exclusion restriction, compliers, always-takers and never-takers. Until then the government's second question stays open."))

s.append(section('4. Earnings, Employment and Heterogeneous Effects'))
s.append(P('<b>Zero earnings:</b> at 30 months, 57.0% of those not offered and 53.1% of those offered earn nothing, and earnings are 0 exactly when someone is not employed. So the ₹9,076 has two parts: ₹6,201 from more people working and ₹2,875 from offered workers earning more (arithmetic only). Comparing the employed alone is not fair, because the offer changes who works: offered workers have 0.11 fewer years of schooling (p = 0.02), while the full groups match.'))
s.append(P("<b>Heterogeneous effects</b> means the effect may differ between kinds of people. We ran the same comparison inside each social category, which is fair because the lottery ran in every group and a category is fixed before the offer."))
s.append(pair(group_chart('employed_30mo' , 100 , lambda c : f'+{c:.1f}' , 'Employment at 30 months (points)' , 'employment.png') ,
              group_chart('earnings_30mo_inr' , 1 , lambda c : f'+₹{c:,.0f}' , 'Earnings at 30 months (₹)' , 'earnings.png')))
s.append(P('Each dot is the difference in means and each line is its 95% CI. The number of people is in brackets.' , 'cell'))
s.append(Spacer(1 , 4))
s.append(table([['Group' , 'Employed, 18 months' , 'Employed, 30 months' , 'Earnings, 18 months' , 'Earnings, 30 months'] ,
                ['General' , '+3.6' , '+3.5' , '+₹6,687' , '+₹8,329'] ,
                ['OBC' , '+2.4 *' , '+5.1' , '+₹6,871' , '+₹9,736'] ,
                ['SC' , '+4.0' , '+2.9 *' , '+₹8,229' , '+₹10,097'] ,
                ['ST' , '+1.5 *' , '+6.3' , '+₹4,091 *' , '+₹11,961']] , [0.2 , 0.2 , 0.2 , 0.2 , 0.2] , center_from=1))
s.append(P('Employment is in percentage points. * does not pass the stricter Bonferroni test explained below.' , 'cell'))
s.append(Spacer(1 , 4))
s.append(B('<b>Does each group gain?</b> Yes. At 30 months every CI is above zero. ST has the largest differences and the widest CIs, as the smallest group.'))
s.append(B("<b>Do groups gain different amounts?</b> We cannot say. We tested all 24 gaps between groups directly and none has p below 0.05 (smallest p = 0.10). ST's lead over General on 30-month earnings is ₹3,632, with a 95% CI from −₹2,849 to ₹10,114."))
s.append(B("<b>Do ST's gains come later?</b> Possibly. Its 18-month effects are not clear, and they rise by 4.8 points and ₹7,870 by 30 months, but neither rise passes the Bonferroni test for these 8 comparisons."))
s.append(B('<b>The risk of many tests:</b> the table holds 16 tests. If there were no real effects and the tests were independent, the chance of at least one false positive would be 56%. So we also applied the Bonferroni test, which judges each result at 0.05 / 16. 12 of the 16 still pass, including all four 30-month earnings effects.'))

s.append(section('5. Inference and Recommendations'))
s.append(table([['Question' , 'Answer' , 'Why'] ,
                ['Continue the programme?' , 'Yes' , 'The offer clearly raises employment and earnings.'] ,
                ['Expand it?' , 'Cannot say yet' , "The gain of ₹9,076 is clearly above zero (statistically significant) and 13.5% of the not offered group's earnings (a meaningful size). Whether it is worth paying for (policy significance) depends on the cost per offer, which is not in the data."] ,
                ['Redesign it?' , 'Look at take-up' , '38% of offers go unused, and each one dilutes the effect per offer. Find out why people decline.'] ,
                ['Target one group?' , 'No' , 'Every group gains, and nothing shows that any group gains more.']] , [0.22 , 0.15 , 0.63]))
s.append(Spacer(1 , 4))
s.append(B("<b>Assumptions:</b> the offer was random (the checks in section 1 support this), one applicant's offer does not change another's outcome, and outcomes were measured the same way for both groups."))
s.append(B('<b>Limits:</b> synthetic data; no costs; the effect of the training itself and the ITT with covariates not done; earnings period not defined; no adjustment for the lottery being run within states.'))
s.append(B('<b>Future evaluations:</b> record the cost per offer, follow people for longer, and use larger samples for small groups.'))


def page_number(canvas , doc):
    canvas.setFont('Body' , 8.5)
    canvas.setFillColor(colors.HexColor(ink2))
    canvas.drawCentredString(A4[0] / 2 , 0.8 * cm , str(doc.page))


out = os.path.join(root , 'docs' , 'ads_assignment_report.pdf')
doc = SimpleDocTemplate(out , pagesize=A4 , leftMargin=1.7 * cm , rightMargin=1.7 * cm , topMargin=1.4 * cm , bottomMargin=1.4 * cm ,
                        title='ADS Assignment Report' , author='Ishan Batra')
doc.build(s , onFirstPage=page_number , onLaterPages=page_number)
print('wrote' , out , doc.page , 'pages')
