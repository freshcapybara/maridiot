import pyglet
from pyglet.gl import *

#from gym.envs.classic_control.rendering import SimpleImageViewer

class ImageViewer(object):
    def __init__(self, display=None, maxwidth=500):
        self.window = None
        self.isopen = False
        self.display = display
        self.maxwidth = maxwidth

    def imshow(self, arr):
        if self.window is None:
            height, width, _channels = arr.shape
            if width > self.maxwidth:
                scale = self.maxwidth / width
                width = int(scale * width)
                height = int(scale * height)
            self.window = pyglet.window.Window(width=width * 2, height=height * 2,
                display=self.display, vsync=True, resizable=True)
            self.width = width
            self.height = height
            self.isopen = True

            @self.window.event
            def on_resize(width, height):
                self.width = width
                self.height = height

            @self.window.event
            def on_close():
                self.isopen = False

        assert len(arr.shape) == 3, "You passed in an image with the wrong number shape"
        image = pyglet.image.ImageData(arr.shape[1], arr.shape[0],
            'RGB', arr.tobytes(), pitch=arr.shape[1]*-3)
        gl.glTexParameteri(gl.GL_TEXTURE_2D,
            gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        texture = image.get_texture()
        texture.width = self.width
        texture.height = self.height
        self.window.clear()
        self.window.switch_to()
        self.window.dispatch_events()
        texture.blit(0, 0) # draw
        self.window.flip()