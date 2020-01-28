import tensorflow as tf

'''Operations'''
def conv2d(x,filters,kernel, strides=1,dilation=1, scope=None, activation=None, reuse=None):
    if activation is None:
        with tf.variable_scope(scope):
            out = tf.layers.conv2d(x, filters, kernel, strides=strides, padding='SAME', dilation_rate=dilation,
                                   kernel_initializer=tf.contrib.layers.xavier_initializer(), name='conv2d',
                                   reuse=reuse)
        return out

    elif activation == 'ReLU':
        with tf.variable_scope(scope):
            out = tf.layers.conv2d(x, filters, kernel, strides=strides, padding='SAME', dilation_rate=dilation,
                                   kernel_initializer=tf.contrib.layers.variance_scaling_initializer(), name='conv2d',
                                   reuse=reuse)
        return tf.nn.relu(out)

    elif activation == 'leakyReLU':
        with tf.variable_scope(scope):
            out = tf.layers.conv2d(x, filters, kernel, strides=strides, padding='SAME', dilation_rate=dilation,
                                   kernel_initializer=tf.contrib.layers.xavier_initializer(), name='conv2d',
                                   reuse=reuse)
        return tf.nn.leaky_relu(out,0.2)

def deconv2d_run(x,filters,kernel,output_shape,strides=2, scope=None, activation=None):

    with tf.variable_scope(scope):
        with tf.variable_scope('deconv2d'):
            weight=tf.get_variable('kernel',shape=[kernel, kernel, filters, x.get_shape().as_list()[-1]])
            bias=tf.get_variable('bias', shape=[filters])


        out = tf.nn.conv2d_transpose(x,weight,output_shape, strides=[1,strides,strides,1])
        out = tf.nn.bias_add(out,bias)
    if activation is None:
        return out

    elif activation == 'ReLU':
        return tf.nn.relu(out)
    elif activation == 'leakyReLU':
        return tf.nn.leaky_relu(out,0.2)

def relu(x):
    return tf.nn.relu(x)

def lrelu(x, alpha=0.2):
    return tf.nn.leaky_relu(x,alpha)

'''Spectral Norm'''
def SNconv(x, channels, kernel, strides=1, scope=None, activation=None):
    with tf.variable_scope(scope):
        kernel=kernel[0]
        w = tf.get_variable("kernel", shape=[kernel, kernel, x.get_shape()[-1], channels], initializer=tf.contrib.layers.variance_scaling_initializer())
        x = tf.nn.conv2d(input=x, filter=spectral_norm(w), strides=[1, strides, strides, 1], padding='SAME')
        bias = tf.get_variable("bias", [channels], initializer=tf.constant_initializer(0.0))
        x = tf.nn.bias_add(x, bias)

        if activation is None:
            return x
        elif activation == 'ReLU':
            return relu(x)
        elif activation == 'leakyReLU':
            return lrelu(x, 0.2)


def spectral_norm(w, iteration=1):
    w_shape = w.shape.as_list()
    w = tf.reshape(w, [-1, w_shape[-1]])

    u = tf.get_variable("u", [1, w_shape[-1]], initializer=tf.truncated_normal_initializer(), trainable=False)

    u_hat = u
    v_hat = None
    for i in range(iteration):
        """
        power iteration
        Usually iteration = 1 will be enough
        """
        v_ = tf.matmul(u_hat, tf.transpose(w))
        v_hat = l2_norm(v_)

        u_ = tf.matmul(v_hat, w)
        u_hat = l2_norm(u_)

    sigma = tf.matmul(tf.matmul(v_hat, w), tf.transpose(u_hat))
    w_norm = w / sigma

    with tf.control_dependencies([u.assign(u_hat)]):
        w_norm = tf.reshape(w_norm, w_shape)

    return w_norm

def l2_norm(v, eps=1e-12):
    return v / (tf.reduce_sum(v ** 2) ** 0.5 + eps)
