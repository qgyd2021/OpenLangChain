#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime

from langchain.agents import Tool


def main():
    def today_date(query: str) -> str:
        now = datetime.now()
        result = now.strftime("%Y-%m-%d %H:%M:%S")
        return result

    tool = Tool(
        name="Today Date",
        func=today_date,
        description="useful for when you want to know the date of today"
    )

    observation = tool.run(
        "",
        verbose=True,
        color="green",
        callbacks=None,
    )
    print('\n')
    print(observation)
    return


if __name__ == '__main__':
    main()
