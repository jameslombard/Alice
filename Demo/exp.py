
def main():

    name = 'powter'
    pow = play(name)


def play(*args):

    if not args:
        print('nothing was sent')
    else:
        for arg in args:
            name = arg
            print(name)

    return(name)

if __name__ == '__main__':
    main()