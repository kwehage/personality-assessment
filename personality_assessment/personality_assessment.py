#!/usr/bin/env python3
from pathlib import Path
import json
import sys
import platform
import string
import matplotlib.pyplot as plt
import argparse
if platform.system() == 'Windows':
    import msvcrt
else:
    import getch


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', default=None)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()

    # Load questions json file
    with (Path(__file__).parent / 'questions.json').open(mode='r') as f:
        questions = json.load(f)


    if arguments.input_file is None:
        # prompt user for input
        print(questions["instructions"])
        i = 0
        while True:
            if i >= len(questions["questions"]):
                break

            print("[%d] %s: [Y, M, N]" % (i + 1, questions["questions"][i]["text"]))
            answer = ''
            while True:
                try:
                    if platform.system() == 'Windows':
                        answer += msvcrt.getch()
                    else:
                        answer += getch.getch()
                    if any([a in answer for a in ["Y", "y", "N", "n", "M", "m"]]):
                        answer = answer[-1].upper()
                        print(answer)
                        break
                    if '\x1b[A' in answer:
                        i -= 2
                        break
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    raise

            answers = ["N", "M", "Y"]
            if any([a == answer for a in answers]):
                question = questions["questions"][i]
                if question.get("reversed", False):
                    answers = answers[::-1]
                question["score"] = answers.index(answer)
                question["answer"] = answer

            i += 1
            if i < 0:
                i = 0
    else:
        with Path(arguments.input_file).open("r") as f:
            i = 0
            for answer in f:
                answer = answer.upper()[0]
                print(i + 1, answer)
                answers = ["N", "M", "Y"]
                if any([a == answer for a in answers]):
                    question = questions["questions"][i]
                    if question.get("reversed", False):
                        answers = answers[::-1]
                    question["score"] = answers.index(answer)
                    question["answer"] = answer
                i += 1

    # compute scores
    scores = {}
    for key in string.ascii_uppercase:
        if key == 'O':
            break
        scores[key] = 0

    for question in questions["questions"]:
        if isinstance(question["category"], list):
            for category in question["category"]:
                scores[category] += question["score"]
        else:
            scores[question["category"]] += question["score"]

    # plot results
    max_scores = [14, 14, 18, 16, 18, 16, 18, 14, 16, 16, 14, 16, 16, 14]
    raw_scores = []
    normalized_scores = []
    titles = []
    with (Path(__file__).parent / 'attributes.json').open(mode='r') as f:
        attributes = json.load(f)

    for key, value in scores.items():
        titles.append(attributes[key]["personality_type"])
        raw_scores.append(value)
    for raw_score, max_score in zip(raw_scores, max_scores):
        normalized_scores.append(float(raw_score) / float(max_score))

    x = range(len(normalized_scores))
    plt.grid(axis='y', zorder=0)
    plt.bar(x, normalized_scores, zorder=3)
    plt.margins(0.15)
    plt.xticks(x, titles, rotation='vertical')
    plt.subplots_adjust(bottom=0.3)
    plt.gca().set_ylim([0, 1.0])
    for i, (normalized_score, raw_score) in \
            enumerate(zip(normalized_scores, raw_scores)):
        plt.text(i, normalized_score + 0.01, str(raw_score),
                 horizontalalignment='center')
    plt.gca().set_ylabel("Normalized score")
    plt.gca().set_title("Personality Self-Portrait Graph")
    plt.savefig("personality_self_portrait.png", dpi=300)

