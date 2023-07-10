#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
数据集:
https://github.com/liuhuanyong/QASystemOnMedicalKG
"""
import argparse
import json
import logging

from project_settings import project_path
import project_settings as settings
from toolbox.neo4j.neo4j_restful import Neo4jRestful
from toolbox.neo4j.converters import escape_string


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--medical_file",
        default=(project_path / "examples/build_kg/medical_kg/data_dir/QASystemOnMedicalKG/data/medical.json").as_posix(),
        type=str
    )

    parser.add_argument("--database", default="medical", type=str)
    parser.add_argument("--username", default="neo4j", type=str)
    parser.add_argument("--password", default="Glory@2021!", type=str)

    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    neo4j_restful = Neo4jRestful(
        database=args.database,
        username=args.username,
        password=args.password,
    )

    with open(args.medical_file, 'r', encoding='utf-8') as f:
        count = 0
        for line in f:
            row = json.loads(line)

            name = row['name']

            desc = row.get('desc', '')
            # category = row.get('category', list())
            prevent = row.get('prevent', '')
            cause = row.get('cause', '')
            symptom = row.get('symptom', '')
            yibao_status = row.get('yibao_status', '')
            get_prob = row.get('get_prob', '')
            easy_get = row.get('easy_get', '')
            get_way = row.get('get_way', '')

            # 关发症, 疾病和疾病之间的关系.
            acompany = row.get('acompany', '')
            cure_department = row.get('cure_department', list())
            cure_way = row.get('cure_way', list())
            cure_lasttime = row.get('cure_lasttime', '')
            cured_prob = row.get('cured_prob', '')
            cost_money = row.get('cost_money', '')
            check = row.get('check', list())
            do_eat = row.get('do_eat', list())
            not_eat = row.get('not_eat', list())
            recommand_eat = row.get('recommand_eat', list())
            recommand_drug = row.get('recommand_drug', list())
            common_drug = row.get('common_drug', list())
            drug_detail = row.get('drug_detail', list())

            # 创建疾病节点 (MERGE 没有时创建)
            statement = """
            MERGE (x:Disease {{ name: "{name}" }}) RETURN x
            """.format(name=name)
            result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            statement = """
            MATCH (x:Disease)
            WHERE x.name="{name}" 
            SET 
            x.desc = "{desc}",
            x.prevent = "{prevent}",
            x.cause = "{cause}",
            x.easy_get = "{easy_get}",
            x.cure_lasttime = "{cure_lasttime}",
            x.cure_department = "{cure_department}",
            x.cure_way = "{cure_way}",
            x.cured_prob = "{cured_prob}",
            x.get_prob = "{get_prob}",
            x.get_way = "{get_way}",
            x.yibao_status = "{yibao_status}",
            x.cost_money = "{cost_money}"
            RETURN x
            """.format(
                name=name,
                desc=escape_string(desc),
                prevent=escape_string(prevent),
                cause=escape_string(cause),
                easy_get=easy_get,
                cure_lasttime=cure_lasttime,
                cure_department=cure_department,
                cure_way=cure_way,
                cured_prob=cured_prob,

                get_prob=get_prob,
                get_way=get_way,
                yibao_status=yibao_status,
                cost_money=cost_money,
            )
            result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            last_department = None
            for department in cure_department:
                # 创建科室节点 (MERGE 没有时创建)
                statement = """MERGE (x:Department {{ name: "{department}" }}) RETURN x""".format(department=department)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                if last_department is not None:
                    # 创建科室的层级关系
                    statement = """
                    MATCH (x:Department), (y:Department) 
                    WHERE x.name="{child_department}" AND y.name="{parent_department}"
                    MERGE (x)-[r:belongs_to {{ name: "属于" }}]->(y) 
                    RETURN r""".format(
                        child_department=department, parent_department=last_department
                    )
                    result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)
                last_department = department

            # 创建疾病与科室之间的关系
            statement = """
            MATCH (x:Disease), (y:Department) 
            WHERE x.name="{disease}" AND y.name="{department}"
            MERGE (x)-[r:belongs_to {{ name: "所属科室" }}]->(y) 
            RETURN r""".format(
                disease=name, department=last_department
            )
            result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for symptom_ in symptom:
                # 创建症状节点 (MERGE 没有时创建)
                statement = """MERGE (x:Symptom {{ name: "{symptom_}" }}) RETURN x""".format(symptom_=symptom_)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建疾病与症状之间的关系
                statement = """
                MATCH (x:Disease), (y:Symptom) 
                WHERE x.name="{disease}" AND y.name="{symptom_}"
                MERGE (x)-[r:has_symptom {{ name: "症状" }}]->(y) 
                RETURN r""".format(
                    disease=name, symptom_=symptom_
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for acompany_ in acompany:
                if acompany_ == name:
                    continue
                # 创建并发症节点 (MERGE 没有时创建)
                statement = """MERGE (x:Disease {{ name: "{acompany_}" }}) RETURN x""".format(acompany_=acompany_)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建疾病与并发症之间的关系
                statement = """
                MATCH (x:Disease), (y:Disease) 
                WHERE x.name="{disease}" AND y.name="{acompany_}"
                MERGE (x)-[r:acompany_with {{ name: "并发症" }}]->(y) 
                RETURN r""".format(
                    disease=name, acompany_=acompany_
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for check_ in check:
                # 创建诊断检查节点 (MERGE 没有时创建)
                statement = """MERGE (x:Check {{ name: "{check_}" }}) RETURN x""".format(check_=check_)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建疾病与诊断检查之间的关系
                statement = """
                MATCH (x:Disease), (y:Check) 
                WHERE x.name="{disease}" AND y.name="{check_}"
                MERGE (x)-[r:need_check {{ name: "诊断检查" }}]->(y) 
                RETURN r""".format(
                    disease=name, check_=check_
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for do_eat_ in do_eat:
                # 创建食物节点 (MERGE 没有时创建)
                statement = """MERGE (x:Food {{ name: "{do_eat_}" }}) RETURN x""".format(do_eat_=do_eat_)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建疾病与食物之间的关系
                statement = """
                MATCH (x:Disease), (y:Food) 
                WHERE x.name="{disease}" AND y.name="{do_eat_}"
                MERGE (x)-[r:do_eat {{ name: "宜吃" }}]->(y) 
                RETURN r""".format(
                    disease=name, do_eat_=do_eat_
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for not_eat_ in not_eat:
                # 创建食物节点 (MERGE 没有时创建)
                statement = """MERGE (x:Food {{ name: "{not_eat_}" }}) RETURN x""".format(not_eat_=not_eat_)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建疾病与食物之间的关系
                statement = """
                MATCH (x:Disease), (y:Food) 
                WHERE x.name="{disease}" AND y.name="{not_eat_}"
                MERGE (x)-[r:not_eat {{ name: "忌吃" }}]->(y) 
                RETURN r""".format(
                    disease=name, not_eat_=not_eat_
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for recommand_eat_ in recommand_eat:
                # 创建食物节点 (MERGE 没有时创建)
                statement = """MERGE (x:Food {{ name: "{recommand_eat_}" }}) RETURN x""".format(recommand_eat_=recommand_eat_)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建疾病与食物之间的关系
                statement = """
                MATCH (x:Disease), (y:Food) 
                WHERE x.name="{disease}" AND y.name="{recommand_eat_}"
                MERGE (x)-[r:recommand_eat {{ name: "推荐食谱" }}]->(y) 
                RETURN r""".format(
                    disease=name, recommand_eat_=recommand_eat_
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for recommand_drug_ in recommand_drug:
                # 创建药品节点 (MERGE 没有时创建)
                statement = """MERGE (x:Drug {{ name: "{recommand_drug_}" }}) RETURN x""".format(recommand_drug_=recommand_drug_)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建疾病与药品之间的关系
                statement = """
                MATCH (x:Disease), (y:Drug) 
                WHERE x.name="{disease}" AND y.name="{recommand_drug_}"
                MERGE (x)-[r:recommand_drug {{ name: "好评药品" }}]->(y) 
                RETURN r""".format(
                    disease=name, recommand_drug_=recommand_drug_
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for common_drug_ in common_drug:
                # 创建药品节点 (MERGE 没有时创建)
                statement = """MERGE (x:Drug {{ name: "{common_drug_}" }}) RETURN x""".format(common_drug_=common_drug_)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建疾病与药品之间的关系
                statement = """
                MATCH (x:Disease), (y:Drug) 
                WHERE x.name="{disease}" AND y.name="{common_drug_}"
                MERGE (x)-[r:common_drug {{ name: "常用药品" }}]->(y) 
                RETURN r""".format(
                    disease=name, common_drug_=common_drug_
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            for drug_detail_ in drug_detail:
                split = drug_detail_.split('(')
                producer_piece = split[:-1]
                drug_name = split[-1]

                producer = '('.join(producer_piece)
                drug_name = drug_name.replace(')', '')

                # 创建药品节点 (MERGE 没有时创建)
                statement = """MERGE (x:Drug {{ name: "{drug_name}" }}) RETURN x""".format(drug_name=drug_name)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建制药者节点 (MERGE 没有时创建)
                statement = """MERGE (x:Producer {{ name: "{producer}" }}) RETURN x""".format(producer=producer)
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

                # 创建制药者与药品之间的关系
                statement = """
                MATCH (x:Producer), (y:Drug) 
                WHERE x.name="{producer}" AND y.name="{drug_name}"
                MERGE (x)-[r:producer_of {{ name: "生产药品" }}]->(y) 
                RETURN r""".format(
                    producer=producer, drug_name=drug_name
                )
                result = neo4j_restful.cmd(statements=statement, do_commit=True, retry_to_ensure_success=True)

            count += 1
            if count % 1000 == 0:
                print("count: {}".format(count))
    return


if __name__ == '__main__':
    main()
