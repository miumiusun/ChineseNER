import os
import pandas as pd

path_data_all = "data/data_all_fangji.csv"  # 原方剂数据集
path_ner_result = "result/ner_predict_test.utf8"    # 命名实体识别结果
path_result = "result/result.csv"   # 存储被识别出来的实体的标准表示
path_data_all_ner = "result/data_all_ner.csv"   # 将命名实体识别结果写到原方剂数据集中
path_new_true_entity = "result/new_true_entity.csv"  # 存储测试集中被识别出的新实体、测试集真实的实体、新实体中正确的实体


def get_data():
    """
    从命名实体识别结果中获取标准的实体词，并输出成CSV、按照不同实体类别排列成不同的列
    :return:
    """
    with open(path_ner_result, "r", encoding="utf-8") as f_ner:
        entity = ""  # 用于保存一个实体
        entity_diseases_list = []    # 用于保存一个方剂的所有病名实体
        entity_pattern_list = []    # 用于保存一个方剂的所有证型实体
        entity_treat_list = []    # 用于保存一个方剂的所有治疗手段实体
        entity_symptom_list = []    # 用于保存一个方剂的所有症状实体
        entity_diseases_all = []    # 用于保存所有方剂的所有病名实体
        entity_pattern_all = []    # 用于保存所有方剂的所有证型实体
        entity_treat_all = []    # 用于保存所有方剂的所有治疗手段实体
        entity_symptom_all = []    # 用于保存所有方剂的所有症状实体
        lines = f_ner.readlines()
        for line in lines:
            char_tag_predict_list = line.split()
            # print("char_tag_predict_list:", char_tag_predict_list)
            if len(char_tag_predict_list) == 0:
                # 每个子列表拼接成字符串，否则若直接输出列表到文件，导致后续读取数据不方便，另外，用join拼接字符串更为方便
                entity_diseases_all.append("、".join(entity_diseases_list))
                entity_pattern_all.append("、".join(entity_pattern_list))
                entity_treat_all.append("、".join(entity_treat_list))
                entity_symptom_all.append("、".join(entity_symptom_list))
                entity_diseases_list = []
                entity_pattern_list = []
                entity_treat_list = []
                entity_symptom_list = []
            elif char_tag_predict_list[-1] == "O":
                continue
            else:
                char = char_tag_predict_list[0]  # 被标注的字符
                predict = char_tag_predict_list[-1]  # NER模型的预测
                predict_loc = predict[0]   # 字符在实体中的位置(B/I/E)
                predict_type = predict[-1]  # 字符所在实体的类型
                if predict_loc == "B" or predict_loc == "I":
                    # print("entity:", entity)
                    entity += char
                elif predict_loc == "E":
                    entity += char
                    if predict_type == "0":
                        entity_diseases_list.append(entity)
                    elif predict_type == "1":
                        entity_pattern_list.append(entity)
                    elif predict_type == "2":
                        entity_treat_list.append(entity)
                    elif predict_type == "3":
                        entity_symptom_list.append(entity)
                    entity = ""
    entity_diseases_all_series = pd.Series(entity_diseases_all, name="NER_diseases")
    entity_pattern_all_series = pd.Series(entity_pattern_all, name="NER_pattern")
    entity_treat_all_series = pd.Series(entity_treat_all, name="NER_treat")
    entity_symptom_all_series = pd.Series(entity_symptom_all, name="NER_symptom")
    entity_all_list = [entity_diseases_all_series, entity_pattern_all_series, entity_treat_all_series,
                       entity_symptom_all_series]
    # print("entity_all_list:", entity_all_list)
    entity_all_series = pd.concat(entity_all_list, axis=1)
    # print("entity_all_series:", entity_all_series)
    entity_all_series.to_csv(path_result, index=False, encoding="utf-8")


def find_new_entity():
    """
    利用集合的差集，寻找识别出的实体中未出现在原实体库中的新实体，用以后续的研究
    :return:
    """
    sets_name_list = ["diseases", "pattern", "treat", "symptom"]    # 四个原实体词库的文件名（病名、证型、治疗手段、症状）
    set_old_list = [set(), set(), set(), set()]  # 用于保存训练集的实体词库中的不同实体的集合列表
    for index, set_name in enumerate(sets_name_list):
        path_set = os.path.join("data", set_name+"_7000.txt")
        with open(path_set, "r", encoding="utf-8") as f_set:
            lines = f_set.readlines()
            for line in lines:
                entity = line.strip()
                set_old_list[index].add(entity)
    # 保存原实体词库中不同实体的四个集合
    set_old_diseases = set_old_list[0]
    set_old_pattern = set_old_list[1]
    set_old_treat = set_old_list[2]
    set_old_symptom = set_old_list[3]
    set_ner_list = [set(), set(), set(), set()]  # 用于保存算法识别出的不同实体词的集合列表
    entity_ner_all = pd.read_csv(path_result)
    for index, set_name in enumerate(sets_name_list):
        for i in range(entity_ner_all.shape[0]):
            entity_ner_string = entity_ner_all["NER_"+set_name].loc[i]
            # print(entity_ner_string)
            if str(entity_ner_string) != "nan":
                entity_ner_list = entity_ner_all["NER_"+set_name].loc[i].split("、")
                # print(entity_ner_list)
                for entity in entity_ner_list:
                    set_ner_list[index].add(entity)
    # print("set_ner_list:", set_ner_list)
    # 用于保存算法识别出的不同实体的四个集合
    set_ner_diseases = set_ner_list[0]
    set_ner_pattern = set_ner_list[1]
    set_ner_treat = set_ner_list[2]
    set_ner_symptom = set_ner_list[3]
    # 得到两个集合的差集,即被发现的新词（比如set_ner_diseases中set_old_diseases中未出现的新实体）
    set_new_diseases = set_ner_diseases - set_old_diseases
    set_new_pattern = set_ner_pattern - set_old_pattern
    set_new_treat = set_ner_treat - set_old_treat
    set_new_symptom = set_ner_symptom - set_old_symptom
    print(set_new_symptom)
    set_new_diseases_series = pd.Series(list(set_new_diseases), name="new_diseases")
    set_new_pattern_series = pd.Series(list(set_new_pattern), name="new_pattern")
    set_new_treat_series = pd.Series(list(set_new_treat), name="new_treat")
    set_new_symptom_series = pd.Series(list(set_new_symptom), name="new_symptom")
    print(set_new_symptom_series)
    set_true_list = [set(), set(), set(), set()]  # 用于保存测试集中不同实体的集合列表
    for index, set_name in enumerate(sets_name_list):
        path_set = os.path.join("data", set_name+"_4000.txt")
        with open(path_set, "r", encoding="utf-8") as f_set:
            lines = f_set.readlines()
            for line in lines:
                entity = line.strip()
                set_true_list[index].add(entity)
    # 用于保存测试集中不同实体的四个集合
    set_true_diseases = set_true_list[0]
    set_true_pattern = set_true_list[1]
    set_true_treat = set_true_list[2]
    set_true_symptom = set_true_list[3]
    set_true_diseases_series = pd.Series(list(set_true_diseases), name="true_diseases")
    set_true_pattern_series = pd.Series(list(set_true_pattern), name="true_treat")
    set_true_treat_series = pd.Series(list(set_true_treat), name="true_treat")
    set_true_symptom_series = pd.Series(list(set_true_symptom), name="true_symptom")
    # 得到被发现的新实体集合与测试集的实体集合之间的交集，则为被发现的新实体中正确的实体
    set_new_true_diseases = set_new_diseases & set_true_diseases
    set_new_true_pattern = set_new_pattern & set_true_pattern
    set_new_true_treat = set_new_treat & set_true_treat
    set_new_true_symptom = set_new_symptom & set_true_symptom
    print(set_new_true_symptom)
    set_new_true_diseases_series = pd.Series(list(set_new_true_diseases), name="new_true_diseases")
    set_new_true_pattern_series = pd.Series(list(set_new_true_pattern), name="new_true_pattern")
    set_new_true_treat_series = pd.Series(list(set_new_true_treat), name="new_true_treat")
    set_new_true_symptom_series = pd.Series(list(set_new_true_symptom), name="new_true_symptom")
    # 通过拼接Series创建最终DataFrame的方法
    new_true_entity_list = [set_new_diseases_series, set_true_diseases_series, set_new_true_diseases_series,
                            set_new_pattern_series, set_true_pattern_series, set_new_true_pattern_series,
                            set_new_treat_series, set_true_treat_series, set_new_true_treat_series,
                            set_new_symptom_series, set_true_symptom_series, set_new_true_symptom_series]
    new_true_entity = pd.concat(new_true_entity_list, axis=1)
    new_true_entity.to_csv(path_new_true_entity, encoding="utf-8")
    # 直接写成一个DataFrame的方法(遗留了列数不匹配的问题)
    # new_true_entity_list = [list(set_new_diseases), list(set_true_diseases), list(set_new_true_diseases),
    #                         list(set_new_pattern), list(set_true_pattern), list(set_new_true_pattern),
    #                         list(set_new_treat), list(set_true_treat), list(set_new_true_treat),
    #                         list(set_new_symptom), list(set_true_symptom), list(set_new_true_symptom)]
    # new_true_entity_name_list = ["new_diseases", "true_diseases", "new_true_diseases",
    #                              "new_pattern", "true_pattern", "new_true_pattern",
    #                              "new_treat", "true_treat", "new_true_treat",
    #                              "new_symptom", "true_symptom", "new_true_symptom"]
    # new_true_entity = pd.DataFrame(new_true_entity_list, columns=new_true_entity_name_list)
    # new_true_entity.to_csv(path_new_true_entity, encoding="utf-8")


def write_to_data():
    """
    将NER算法的实体识别结果写入到原方剂数据集中
    :return:
    """
    data_all = pd.read_csv(path_data_all)
    result = pd.read_csv(path_result)
    # print(result)
    print(result.info())
    data_all.insert(11, "NER_diseases", None)
    data_all.insert(12, "NER_pattern", None)
    data_all.insert(13, "NER_treat", None)
    data_all.insert(14, "NER_symptom", None)
    data_all["NER_diseases"] = result["NER_diseases"]
    data_all["NER_pattern"] = result["NER_pattern"]
    data_all["NER_treat"] = result["NER_treat"]
    data_all["NER_symptom"] = result["NER_symptom"]
    print(data_all.info())
    data_all.to_csv(path_data_all_ner, encoding="utf-8")


if __name__ == "__main__":
    get_data()
    find_new_entity()
    # write_to_data()
