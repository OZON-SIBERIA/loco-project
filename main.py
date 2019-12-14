import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import random


def open_data(name):
    f = open(name)
    lines = f.read().split('\n')
    ret = []
    for i in range(0, len(lines) - 1):
        split = lines[i].split('\t')
        new_rec = [int(split[0]), float(split[1]), float(split[2]), int(split[3])]
        ret.append(new_rec)
    return ret


def filter_data_const(in_data):
    ret = []
    j = 1  # 1 rpm 2 power
    s = 0
    tol = 0.03
    prev = in_data[0][j]
    for rec in in_data:
        if (rec[j] - prev) / prev < tol:
            s += 1
        else:
            s = 0
        if s > 10:
            ret.append(rec)
        prev = rec[j]
    return ret


def filter_data_kontr(in_data):
    ret = []
    prev = in_data[0][3]
    s = 0
    for rec in in_data:
        # if мощность более 200 кВт, обороты не нулевые
        # и контроллер не нулевой и равен предыдущему
        if rec[2] > 200 and rec[1] > 0 and 0 < prev == rec[3]:
            s += 1
        else:
            s = 0
        if s > 10:
            ret.append(rec)
        prev = rec[3]
    return ret


def filter_data_date_first(in_data):
    ret = []
    timestamp = datetime.fromtimestamp(in_data[0][0])
    for rec in in_data:
        if datetime.fromtimestamp(rec[0]).date() == timestamp.date():
            ret.append(rec)
    return ret


def filter_data_date_last(in_data):
    ret = []
    timestamp = datetime.fromtimestamp(in_data[len(in_data)-1][0])
    for rec in in_data:
        if datetime.fromtimestamp(rec[0]).date() == timestamp.date():
            ret.append(rec)
    return ret


def clusterise(in_data):
    rpms = []
    powers = []
    counts = []
    ret = []
    for i in range(0, 16):
        rpms.append([])
        powers.append([])
        counts.append(0)
    for i in range(0, len(in_data)-1):
        rpms[in_data[i][3]].append(in_data[i][1]) # обороты
        powers[in_data[i][3]].append(in_data[i][2]) # мощность
        counts[in_data[i][3]] += 1 # число точек
    for i in range(0, 16):
        if counts[i] > 0:
            ret.append([np.median(rpms[i]), np.median(powers[i])])
            #ret.append([np.median(rpms[i]), np.median(powers[i]), np.var(rpms[i]), np.var(powers[i])])
        #ret.append([rpms[i] /= counts[i], powers[i] /= counts[i], counts[i]])
    return ret


def get_panes(in_clusters):
    ret = [in_clusters[0][0] - (in_clusters[1][0] - in_clusters[0][0]) / 2]
    for i in range(0, len(in_clusters)-1):
        ret.append(in_clusters[i][0]+(in_clusters[i+1][0] - in_clusters[i][0]) / 2)
    ret.append(in_clusters[len(in_clusters)-1][0] + (in_clusters[len(in_clusters)-1][0] - in_clusters[len(in_clusters)-2][0]) / 2)
    return ret


def get_pane(rpm, panes):
    ret = -1
    for j in range(0, len(panes)-1):
        if panes[j] <= rpm < panes[j + 1]:
            return j
    return ret


def get_kontr(rpm):
    ret = -1
    for j in range(0, 14):
        if bottom_x[j] <= rpm < top_x[j + 1]:
            return j+1
    return ret


def get_above(rpm, power):
    kontr = get_kontr(rpm)
    p1 = np.asarray([top_x[kontr-1], top_y[kontr-1]])
    p2 = np.asarray([top_x[kontr], top_y[kontr]])
    p3 = np.asarray([rpm, power])
    return np.cross(p2 - p1, p3 - p1) / np.linalg.norm(p2 - p1)


def get_below(rpm, power):
    kontr = get_kontr(rpm)
    p1 = np.asarray([bottom_x[kontr-1], bottom_y[kontr-1]])
    p2 = np.asarray([bottom_x[kontr], bottom_y[kontr]])
    p3 = np.asarray([rpm, power])
    return np.cross(p2 - p1, p1 - p3) / np.linalg.norm(p2 - p1)


def set_states_limits(in_clusters, panes, states):
    u0 = 0
    u1 = 30
    for c in in_clusters:
        k = get_pane(c[0], panes)
        k1 = get_kontr(c[0])
        a = get_above(c[0], c[1])
        b = get_below(c[0], c[1])
        # print("{} rpm {} kW {} k {} a {} b".format(c[0], c[1], k1, a, b))
        if a >= u1 or b >= u1:
            states[k] = 2
        elif a > u0 or b > u0:
            states[k] = 1
        else:
            states[k] = 0


# def on_click(event):
#     p = get_pane(event.xdata)
#     states[p] = (states[p]+1)%3
#     plt.cla()
#     redraw(fig)


def redraw(in_fig, panes, states, num):
    ax = in_fig.gca()
    plt.grid()
    for pane in panes:
        plt.axvline(x=pane, c='black')
    colors = ['green', 'yellow', 'red']
    for p in range(0, len(states)):
        plt.axvspan(panes[p], panes[p + 1], color=colors[states[p]], alpha=0.15)
    ax.scatter(even_x, even_y, c='navy', s=4)
    ax.scatter(odd_x, odd_y, c='darkcyan', s=4)
    ax.scatter(c_x, c_y, c='red', s=12)
    #line1, = ax.plot(center_x, center_y, c='black')
    #line1.set_dashes([10, 5])
    line2, = ax.plot(bottom_x, bottom_y, c='coral')
    line2.set_dashes([10, 5])
    line3, = ax.plot(top_x, top_y, c='green')
    line3.set_dashes([10, 5])
    ax.set_xlabel(u'Частота вращения, об/мин')
    ax.set_ylabel(u'Мощность, кВт')
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    plt.show()
    #in_fig.savefig("grafs/image_{}".format(num))


center_x = [400, 850]
center_y = [75, 1775]
bottom_x = [400, 435, 465, 495, 530, 560, 590, 625, 660, 690, 720, 755, 785, 820, 850]
bottom_y = [40, 100, 190, 265, 350, 425, 520, 630, 750, 880, 1000, 1160, 1320, 1530, 1750]
top_x = [415, 450, 480, 510, 545, 575, 605, 640, 675, 705, 735, 770, 800, 835, 860]
top_y = [110, 240, 350, 470, 620, 770, 890, 1020, 1140, 1250, 1370, 1500, 1600, 1730, 1800]

even_x = []
even_y = []
odd_x = []
odd_y = []
c_x = []
c_y = []


def main(num):
    unfiltered = open_data("lokodata_{}.txt".format(num))
    print('Количество записей:\n%i' % len(unfiltered))
    filtered = filter_data_kontr(unfiltered)
    #filtered = filter_data_const(filtered1)
    print('Количество записей после фильтрации: %i' % len(filtered))
    records_first = filter_data_date_first(filtered)
    print('Количество записей за первый день: %i' % len(records_first))
    print(datetime.utcfromtimestamp(filtered[0][0]).date())
    records_last = filter_data_date_last(filtered)
    print('Количество записей за последний день: %i' % len(records_last))
    print(datetime.utcfromtimestamp(filtered[len(filtered)-1][0]).date())
    clusters = clusterise(filtered)
    panes = get_panes(clusters)
    states = []
    for i in range(0, len(panes)-1):
        states.append(0)
    set_states_limits(clusters, panes, states)

    # отображение
    # разделение на чётные и нечётные позиции контроллера
    even_x.clear()
    even_y.clear()
    odd_x.clear()
    odd_y.clear()
    c_x.clear()
    c_y.clear()
    for record in filtered:
        if record[3] % 2 == 0:
            even_x.append(record[1])
            even_y.append(record[2])
        else:
            odd_x.append(record[1])
            odd_y.append(record[2])

    for line in clusters:
        if line[0] > 0 and line[1] > 0:
            c_x.append(line[0])
            c_y.append(line[1])

    fig = plt.figure()
    #fig.canvas.mpl_connect('button_press_event', on_click)
    redraw(fig, panes, states, num)


main(18)
