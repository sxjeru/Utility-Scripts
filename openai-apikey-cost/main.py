# 修改自 https://www.jeypop.co.uk/ai/handling-openai-api-cost-retrieval-changes/

import datetime, time
import json
import requests

model_costs = {
    "gpt-3.5-turbo-instruct": {"context": 0.0015, "generated": 0.002},
    "gpt-3.5-turbo-0301": {"context": 0.0015, "generated": 0.002},
    "gpt-3.5-turbo-0613": {"context": 0.0015, "generated": 0.002},
    "gpt-3.5-turbo-16k": {"context": 0.003, "generated": 0.004},
    "gpt-3.5-turbo-16k-0613": {"context": 0.003, "generated": 0.004},
    "gpt-4-0314": {"context": 0.03, "generated": 0.06},
    "gpt-4-0613": {"context": 0.03, "generated": 0.06},
    "gpt-4-32k": {"context": 0.06, "generated": 0.12},
    "gpt-4-32k-0314": {"context": 0.06, "generated": 0.12},
    "gpt-4-32k-0613": {"context": 0.06, "generated": 0.12},
    "text-davinci:003": {"context": 0.02, "generated": 0.02},
    "whisper-1": {
        "context": 0.006 / 60,
        "generated": 0,
    },  # Cost is per second, so convert to minutes
}

url = "https://api.openai.com/v1/usage"
# api_key = os.getenv("OPENAI_API_KEY")
proxies = {
    "http": "http://127.0.0.1:1082",
    "https": "http://127.0.0.1:1082"
}

def get_daily_cost(date, headers):
    params = {"date": date}
    while True:
        try:
            response = requests.get(url, headers=headers, params=params, proxies=proxies)
            response.raise_for_status()
            usage_data = response.json()["data"]
            whisper_data = response.json()["whisper_api_data"]
            daily_cost = 0
            for data in usage_data + whisper_data:
                model = data.get("model_id") or data.get("snapshot_id")
                model = model.split(":")[0]
                if model in model_costs:
                    if "num_seconds" in data:
                        cost = data["num_seconds"] * model_costs[model]["context"]
                    else:
                        context_tokens = data["n_context_tokens_total"]
                        generated_tokens = data["n_generated_tokens_total"]
                        cost = (context_tokens / 1000 * model_costs[model]["context"]) + (
                            generated_tokens / 1000 * model_costs[model]["generated"]
                        )
                    daily_cost += cost
                else:
                    print("[red]model not defined, please add model and associated costs to model_costs object[/red]")
                    return None
            return daily_cost
        except requests.HTTPError as err:
            if err.response.status_code == 429:
                print("[red]Rate limit exceeded. Sleeping for 69 seconds...[/red]")
                time.sleep(69)
                continue
            print(f"Request failed: {err}")
            return None
        except KeyError as err:
            print(f"Missing key in API response: {err}")
            return None

def get_costs(start_date, end_date, id, headers):
    try:
        with open(f"costs {id}.json", "r") as file:
            stored_costs_dict = json.load(file)
    except FileNotFoundError:
        stored_costs_dict = {}
    total_cost = 0
    for date in range(start_date.toordinal(), end_date.toordinal() + 1):
        date_obj = datetime.date.fromordinal(date)
        date_str = date_obj.isoformat()
        if (
            date_str in stored_costs_dict
            # and date_str != datetime.date.today().isoformat()
            and date_str != stored_costs_dict[date_str]['query_time'][:10]
        ):
            daily_cost = stored_costs_dict[date_str]["cost"]
        else:
            daily_cost = get_daily_cost(date_str, headers)
            if daily_cost is None:
                return None
            query_time = datetime.datetime.now(datetime.timezone.utc)
            stored_costs_dict[date_str] = {
                "cost": daily_cost,
                "query_time": query_time.isoformat(),
            }
        total_cost += daily_cost
    with open(f"costs {id}.json", "w") as file:
        json.dump(stored_costs_dict, file, indent=4)
    return total_cost

import csv
def update_records(id, cost):
    with open("records.csv", "a+", newline="") as file:
	file.seek(0)
        reader = reversed(list(csv.reader(file)))
        flag = True
        for existing_row in reader:
            if int(existing_row[0]) == id:
                if float(existing_row[1]) == cost:
                    flag = False
                    print(f"\nCost 无变化")
                old_cost = float(existing_row[1])
                break
        if flag:
	    file.seek(0, 2)
            writer = csv.writer(file)
            writer.writerow([id, cost, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            print(f"\n记录已更新: {old_cost} -> {cost}")
