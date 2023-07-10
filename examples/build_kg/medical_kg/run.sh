#!/usr/bin/env bash

# sh run.sh --stage 1 --stop_stage 1 --system_version windows
# sh run.sh --stage 2 --stop_stage 2 --system_version windows

system_version=windows
verbose=true;
stage=-1
stop_stage=3


# parse options
while true; do
  [ -z "${1:-}" ] && break;  # break if there are no arguments
  case "$1" in
    --*) name=$(echo "$1" | sed s/^--// | sed s/-/_/g);
      eval '[ -z "${'"$name"'+xxx}" ]' && echo "$0: invalid option $1" 1>&2 && exit 1;
      old_value="(eval echo \\$$name)";
      if [ "${old_value}" == "true" ] || [ "${old_value}" == "false" ]; then
        was_bool=true;
      else
        was_bool=false;
      fi

      # Set the variable to the right value-- the escaped quotes make it work if
      # the option had spaces, like --cmd "queue.pl -sync y"
      eval "${name}=\"$2\"";

      # Check that Boolean-valued arguments are really Boolean.
      if $was_bool && [[ "$2" != "true" && "$2" != "false" ]]; then
        echo "$0: expected \"true\" or \"false\": $1 $2" 1>&2
        exit 1;
      fi
      shift 2;
      ;;

    *) break;
  esac
done

work_dir="$(pwd)"

data_dir="${work_dir}/data_dir"

mkdir -p "${data_dir}"

export PYTHONPATH="${work_dir}/../../.."

if [ $system_version == "windows" ]; then
  #source /data/local/bin/OpenLangChain/bin/activate
  alias python3='C:/Users/tianx/PycharmProjects/virtualenv/OpenLangChain/Scripts/python.exe'
elif [ $system_version == "centos" ] || [ $system_version == "ubuntu" ]; then
  alias python3='/data/local/bin/OpenLangChain/bin/python3'
fi


if [ ${stage} -le -1 ] && [ ${stop_stage} -ge -1 ]; then
  $verbose && echo "stage -1: install neo4j"
  cd "${work_dir}" || exit 1;

  # windows
  # 安装 neo4j 软件.
  # 创建 project. Name: KBQA, Password: Glory@2021!
  # 启动 project. Start.
  # 在 project 内创建数据库.
  # 在软件中创建数据库. Add Local DBMS (database manage system)
  # MedicalKG

  # Neo4j 安装 APOC
  # https://www.ngui.cc/zz/1862560.html


fi


if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
  $verbose && echo "stage 0: download data"
  cd "${data_dir}" || exit 1;

  git clone "https://github.com/liuhuanyong/QASystemOnMedicalKG"

  mv QASystemOnMedicalKG/data/medical.json medical.json
  rm -rf QASystemOnMedicalKG

fi


if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
  $verbose && echo "stage 1: build and write in data"
  cd "${work_dir}" || exit 1;

  python3 1.build_kg.py \
  --medical_file "${data_dir}/medical.json" \
  --database medical \
  --username neo4j \
  --password Glory@2021!

fi


if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
  $verbose && echo "stage 2: query test"
  cd "${work_dir}" || exit 1;

  python3 2.query_kg.py \
  --database medical \
  --username neo4j \
  --password Glory@2021! \
  --verbose

fi
