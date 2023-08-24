#!/usr/bin/env bash

# sh run.sh --stage 1 --stop_stage 1 --system_version windows

system_version=centos
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

export PYTHONPATH="${work_dir}/../../../.."


if [ $system_version == "windows" ]; then
  #source /data/local/bin/OpenLangChain/bin/activate
  alias python3='C:/Users/tianx/PycharmProjects/virtualenv/OpenLangChain/Scripts/python.exe'
elif [ $system_version == "centos" ] || [ $system_version == "ubuntu" ]; then
  alias python3='/data/local/bin/OpenLangChain/bin/python3'
fi


if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
  $verbose && echo "stage 0: download pdf"
  cd "${work_dir}" || exit 1;

  wget "https://raw.githubusercontent.com/brunogarcia/langchain-titanic-sqlite/main/titanic.db"

fi


if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
  $verbose && echo "stage 1: run"
  cd "${work_dir}" || exit 1;

  python3 sql_database_chain.py

fi

