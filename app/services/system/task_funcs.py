def count_total_persons_and_age_by_gender(data: dict, gender: str) -> dict:
    total_age = 0
    persons = 0
    for person in data['data']:
        if person['demographics']['gender'] == gender:
            total_age += int(person['demographics']['age']['mean'])
            persons += 1

    return {"persons": persons, "age": total_age}


def count_average_age(total_age: int, total_persons) -> float:
    return total_age / total_persons
