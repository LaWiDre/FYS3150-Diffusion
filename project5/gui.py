import ui_tools as ui
import frontend

def new_diffuser(vals = None):

    num = (float, int)
    quantities = ["xc", "xb", "T", "dt", "D", "N", "dx"]
    labels = ["Initial Conditions", "Boundary Conditions",
    "Simulation Runtime (s)", "Time-Step (s)", "No. of Dimensions",
    "Dimensionwise Array Length", "Position-Step (m)"]
    types = [num, num, num, num, int, int, num]
    minima = [None, None, 0, 0, 1, 0, 0, None]
    msg1 = " number!"
    msg2 = " number greater than zero!"
    msg3 = "n integer greater than one!"
    msg4 = "n integer greater than zero!"
    errors = [msg1, msg1, msg2, msg2, msg3, msg4, msg2, msg1]
    retry = False
    if vals is None:
        vals = []
        for q, l, t, m, e in zip(quantities, labels, types, minima, errors):
            while True:
                ui.clear()
                if retry is True:
                    retry = False
                    print("Invalid input. Must be a{}".format(e))
                val = ui.get_input(msg = '{}: '.format(l), types = t)
                try:
                    val = float(val)
                    if int(val) == val:
                        val = int(val)
                except:
                    retry = True
                    continue
                if m is not None and val <= m:
                    retry = True
                else:
                    vals.append(val)
                    break
    options = {}
    options["C"] = "Confirm"
    cancel = False
    while True:
        for i in range(len(quantities)):
            q = quantities[i]
            options["{:d}".format(i+1)] = "{:>27s}= {:<27g}".format(labels[i], vals[i])
        res = ui.select_from_menu(options, title = 'Modify or Confirm')
        if res == "Confirm":
            return vals
        elif res == "return":
            return "return"
        else:
            i = labels.index((res.split("=")[0]).strip())
            newval = vals[i]
            while True:
                ui.clear()
                if retry is True:
                    retry = False
                    print("Invalid input. Must be a{}".format(errors[i]))
                val = ui.get_input(msg = '{}: '.format(labels[i]), types = types[i])
                try:
                    val = float(val)
                    if int(val) == val:
                        val = int(val)
                except:
                    retry = True
                    continue
                if minima[i] is not None and val <= minima[i]:
                    retry = True
                else:
                    vals[i] = val
                    break

def main():
    res = "main_menu"
    diffuser = None
    while True:
        if res == "main_menu":
            if diffuser is not None:
                options = {"1":"Edit Diffuser", "2":"Run Simulation"}
            else:
                options = {"1":"New Diffuser"}
            res = ui.select_from_menu(options, title = 'Main Menu', back = False)
        elif res == "New Diffuser":
            res = new_diffuser()
            if isinstance(res, str) and res == "return":
                res = "main_menu"
            else:
                diffuser = frontend.Diffuser(res[0], res[1], res[2], res[3], res[4], res[5], res[6])
                diffuser._write_data()
                diffuser._call_backend()
                raise NotImplementedError("Complete Backend Then Create Algorithm Selector")
        else:
            print(res)
            break

main()
