import sys

def main(dict_fp, tweet_fp):
    emoto_set = set([line.strip() for line in open(dict_fp)])

    tok_list = [line.split(' ')[0] for line in open(tweet_fp)]
    count = 0
    for i in range(len(tok_list) - 1):
        if tok_list[i] == '&lt;':
            combo = '<'
        else:
            combo = tok_list[i]
        if tok_list[i + 1] == '&lt;':
            combo += '<'
        else:
            combo += tok_list[i + 1]


        if combo in emoto_set:
            count += 1
            print count, combo

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
