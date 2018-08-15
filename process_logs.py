dataset = ["pku","msr","cityu","as","ctb"]
for i in range(5):
    logs_dir = "Logs/"+dataset[i]+"/logs_output.txt"
    logs_dir_new = "Logs/%s/logs_output_%s.txt" % (dataset[i], dataset[i])
    fo1 = open(logs_dir, "r")
    fo2 = open(logs_dir_new, "a")
    text = fo1.readline()
    text = text.replace("/n", "\n")
    fo2.write(text)
    fo1.close()
    fo2.close()
