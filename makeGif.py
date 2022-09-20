import imageio.v2 as imageio

def makeGif(angle):
    images = []
    BASE_NAME = 'static/img/angle-'
    try:
        for i in range(0, angle+11, 5):
            images.append(imageio.imread(BASE_NAME + str(i) + '-.png'))
        for i in range(angle+10, angle-6, -5):
            images.append(imageio.imread(BASE_NAME + str(i) + '-.png'))
        for i in range( angle-5, angle+1, 5):
            images.append(imageio.imread(BASE_NAME + str(i) + '-.png'))
    except:
        images = []
        for i in range(0, angle+1, 5):
            images.append(imageio.imread(BASE_NAME + str(i) + '-.png'))
    imageio.mimsave('static/img/movie.gif', images,loop=1,fps=24)

if __name__ == '__main__':
    # makeGif(70)
    ...