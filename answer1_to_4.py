"""
###################################################################################################
    Last updated on Sun May 12 15:44:14 2019
    This code contains all the answer to question 1 to 4, and it's called inside the
    main function
    
    Structure of my CNN Network
        Input Layer
        first conv layer(with relu)
        pooling layer
        second conv layer(with relu)
        pooling layer
        Flatten layer
        fully connected layer1
        output layer(with softmax)
    AdamOptimizer with cross entropy loss is used for learning
    
    @author: gaddisa olani
###################################################################################################
"""
import os
import math
import numpy as np
import tensorflow as tf
import preprocess_it as dataset
import matplotlib.pyplot as plt


def add_new_weights(shape):
    return tf.Variable(tf.truncated_normal(shape, stddev=0.05))
def add_new_bias_term(length):
    return tf.Variable(tf.constant(0.05, shape=[length]))


def add_convolution_layer(input,num_input_channels,kernel_size,number_kernels,use_pooling=True):

    shape = [kernel_size, kernel_size, num_input_channels, number_kernels]
    weights = add_new_weights(shape=shape)
    biases = add_new_bias_term(length=number_kernels)
    layer = tf.nn.conv2d(input=input,filter=weights,strides=[1, 1, 1, 1],padding='SAME')
    layer += biases
     # apply pooling of 2X2
    if use_pooling:
       
        layer = tf.nn.max_pool(value=layer,ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1],padding='SAME')
    layer = tf.nn.relu(layer)
    return layer, weights


def flatten_layer(layer):
    # Get the shape of the input layer.
    layer_shape = layer.get_shape()

   
    num_features = layer_shape[1:4].num_elements()
    
    output_flatten_layer = tf.reshape(layer, [-1, num_features])

    return output_flatten_layer, num_features

"""
 define a function to create a fully connected layer
 the input is the output of the previous layer, and Relu is used as activation function
"""
def add_fully_connected_layer(input,num_inputs,num_outputs,output_layer=True): 
    weights = add_new_weights(shape=[num_inputs, num_outputs])
    biases = add_new_bias_term(length=num_outputs)
    # l=XW+b
    layer = tf.matmul(input, weights) + biases

    # don't apply relu to the output layer
    if output_layer==False:
        layer = tf.nn.relu(layer)

    return layer,weights
def start_training_evaluating(num_iterations):
    # Ensure we update the global variable rather than a local copy.
    global total_iterations

    # Start-time used for printing time-usage below.
    
    best_val_loss = float("inf")
    patience = 0

    for i in range(total_iterations,total_iterations + num_iterations):
        x_batch, y_true_batch, _, cls_batch = data.train.next_batch(train_batch_size)
        x_valid_batch, y_valid_batch, _, valid_cls_batch = data.valid.next_batch(train_batch_size)
        x_batch = x_batch.reshape(train_batch_size, img_size_flat)
        x_valid_batch = x_valid_batch.reshape(train_batch_size, img_size_flat)
        """
        tf placeholder for TensorFlow graph to put batch in to a dict.
        Evaluate on validation set as I partition the training set to 80/20
        """
        feed_dict_train = {x: x_batch,y_true: y_true_batch}
        feed_dict_validate = {x: x_valid_batch,y_true: y_valid_batch}
        
        
        """
        Evaluate the entire test set at each iteration
        """
        test_datas=test_data.images
        x_test = test_datas.reshape(test_datas.shape[0], img_size_flat)
        feed_dict_test = {x: x_test, y_true: test_data.labels}
        
        
        session.run(optimizer, feed_dict=feed_dict_train)
        
        # Print status at end of each epoch (defined as full pass through training dataset).
        if i % int(data.train.num_examples/train_batch_size) == 0: 
            val_loss = session.run(cost, feed_dict=feed_dict_validate)
            training_loss,training_accuracy = session.run([cost,accuracy], feed_dict=feed_dict_train)
            test_loss=session.run(cost, feed_dict=feed_dict_test)
            test_acc=session.run(accuracy, feed_dict=feed_dict_test)
            
            
            training_accuracy_cache.append(training_accuracy)
            test_accuracy_cache.append(test_acc)
    
    
            #training_loss_cache.append(train_loss)
            training_loss_cache.append(training_loss)
            test_loss_cache.append(test_loss)
            
            
            
            epoch = int(i / int(data.train.num_examples/train_batch_size))
            msg = "Epoch {0} --- Training Accuracy: {1:>6.1%}, Test Accuracy: {2:>6.1%}, Training Loss:{3:.3f},Test Loss: {4:.3f}"

            print(msg.format(epoch + 1, training_accuracy, test_acc,training_loss, test_loss))
            

            if early_stopping:    
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience = 0
                else:
                    patience += 1

                if patience == early_stopping:
                    break

    # Update the total number of iterations performed.
    total_iterations += num_iterations

def plot_images(images, cls_true, cls_pred=None):
    images=images
    cls_true=cls_true
    xlabel = "True: {0}, Pred: {1}".format(cls_true, cls_pred)
    plt.title(xlabel)
    plt.imshow(images.reshape(img_size, img_size, num_channels))
    plot_conv_layer(layer=first_conv_layer, image=images,title="First conv layer")
    plot_conv_layer(layer=second_conv_layer, image=images,title="second conv Layer")

#plot the training  accuracy vs validation accuracy
def plot_accuracy_loss():
    
    #plot the training loss vs test loss   
    plt.plot(training_loss_cache,label='training loss')
    plt.plot(test_loss_cache,label='test loss')
    plt.legend(loc='best')
    plt.xlabel("epochs")
    plt.ylabel("Cross Entropy")
    plt.title("Learning Curve")
    plt.grid()
    plt.show()
    

    #plot the training accuracy vs test accuracy
    plt.plot(training_accuracy_cache,label='training acc')
    plt.plot(test_accuracy_cache,label='test acc')
    plt.legend(loc='best')
    plt.xlabel("epochs")
    plt.ylabel("Accuracy")
    plt.title("Accuracy")
    plt.grid()
    plt.show()



def plot_activation_of_conv_layer():

    # Number of images in the test-set.
    num_test = len(data.valid.images)
    cls_pred = np.zeros(shape=num_test, dtype=np.int)

    # Now calculate the predicted classes for the batches.
    i = 0

    while i < num_test:
        # The ending index for the next batch is denoted j.
        j = min(i + train_batch_size, num_test)
        
        reshape_size = train_batch_size
        if data.valid.images[i:j, :].shape[0] < reshape_size:
            reshape_size = data.valid.images[i:j, :].shape[0] 
        try:
            images = data.valid.images[i:j, :].reshape(reshape_size, img_size_flat)
        except:
            print (i)
        
        # Get the associated labels.
        labels = data.valid.labels[i:j, :]

        # Create a feed-dict with these images and labels.
        feed_dict = {x: images,y_true: labels}

        # Calculate the predicted class using TensorFlow.
        cls_pred[i:j] = session.run(y_pred_cls, feed_dict=feed_dict)
        i = j
        
    cls_true = np.array(data.valid.cls)
    cls_pred = np.array([training_classes[x] for x in cls_pred]) 

    # Create a boolean array whether each image is correctly classified.
    correct = (cls_true == cls_pred)
    
    r=(correct == True)
    images = data.valid.images[r]
    
    # Get the predicted  for those images.
    cls_pred = cls_pred[r]
    # Get the true classes for those images.
    cls_true = data.valid.cls[r]
    
    plot_images(images=images[0],cls_true=cls_true[0],cls_pred=cls_pred[0])
    
#plot conv layer 

def plot_conv_layer(layer, image,title):
    
    image = image.reshape(img_size_flat)
    feed_dict = {x: [image]}
    values = session.run(layer, feed_dict=feed_dict)
    number_kernels = values.shape[3]
    num_grids = math.ceil(math.sqrt(number_kernels))
    
    # Create figure with a grid of sub-plots.
    fig, axes = plt.subplots(num_grids, num_grids)

    # Plot the output images of all the filters.
    for i, ax in enumerate(axes.flat):
        if i<number_kernels:
            img = values[0, :, :, i]
            # Plot image.
            ax.imshow(img, interpolation='nearest', cmap='binary')
        
        # Remove ticks from the plot.
        ax.set_xticks([])
        ax.set_yticks([])
    plt.show()
    print("The output of",title)
    

def plot_histogram_con_layer_weights(weight,title):
    w = session.run(weight)
    results, edges = np.histogram(w,  bins=128,density=True)
    binWidth = edges[1] - edges[0]
    plt.bar(edges[:-1], results*binWidth, binWidth)
    plt.title(title)
    plt.xlabel('Value')
    plt.ylabel('Probability')
    plt.show()


#plot a histogram for each convolutional layer weights
def plot_histogram_of_weights():
    title="Histogram of Convolutional layer 1"
    plot_histogram_con_layer_weights(weights_conv1,title)
    title="Histogram of Convolutional layer 2"
    plot_histogram_con_layer_weights(weights_conv2,title)
    
    title="Histogram of Dense 1"
    plot_histogram_con_layer_weights(weights_fc1,title)
    
    title="Histogram of Output Layer"
    plot_histogram_con_layer_weights(weights_fc2,title)

def start_training():
        
    '''initial parameters, to make it accessible outside of this function 
         I make all of them global variable '''
    global total_iterations,kernel_size1,number_kernels1,kernel_size2,fc_size,num_channels,img_size
    global img_size_flat,img_shape,train_batch_size,validation_size,training_accuracy_cache
    global training_loss_cache,test_loss_cache,training_classes,num_train_classes
    global early_stopping,test_classes,num_test_classes,train_path,test_path,data,test_data,x,x_image
    global y_true,y_true_cls,first_conv_layer, weights_conv1,second_conv_layer, weights_conv2
    global output_flatten_layer, num_features,layer_fc1,weights_fc1,layer_fc2,weights_fc2,y_pred,y_pred_cls
    global cross_entropy,cross_entropy,optimizer,correct_prediction,accuracy,session,cost
    global test_accuracy_cache,n_it
    #initialization of global variables
    kernel_size1 = 8 
    number_kernels1 = 16
    kernel_size2 = 8
    number_kernels2 = 16
    fc_size = 128            
    num_channels = 3
    img_size = 128
    # Size of image when flattened to a single dimension
    img_size_flat = img_size * img_size * num_channels
    # Tuple with height and width of images used to reshape arrays.
    img_shape = (img_size, img_size)
    train_batch_size = 256
    validation_size = .20
    n_it=1000
    '''a list used to record the value of cross entropy loss and accuracy at each iteration'''
    
    training_accuracy_cache=list()
    test_accuracy_cache=list()
    training_loss_cache=list()
    test_loss_cache=list()
    total_iterations = 0
    
    """
    Iterate through the folder and get folder name and save it
    # class info
    
    """
    
    #read folders and class labels
    training_classes = list()
    for root, dirs, files in os.walk("data/train", topdown=False):
        for name in dirs:
            training_classes.append(name)
    
    num_train_classes = len(training_classes)
    
    
    #read folders and class labels testset
    test_classes = list()
    for root, dirs, files in os.walk("data/train", topdown=False):
        for name in dirs:
            test_classes.append(name)
    
    num_test_classes = len(test_classes)
    
    

    early_stopping = None  # use None if you don't want to implement early stoping
    
    train_path = 'data/train/'
    test_path = 'data/test/'
    
    data = dataset.read_train_sets(train_path, img_size, training_classes, validation_size=validation_size)
    test_data=dataset.read_test_set(test_path, img_size,test_classes)
    
    x = tf.placeholder(tf.float32, shape=[None, img_size_flat], name='x')
    x_image = tf.reshape(x, [-1, img_size, img_size, num_channels])
    y_true = tf.placeholder(tf.float32, shape=[None, num_train_classes], name='y_true')
    y_true_cls = tf.argmax(y_true, axis=1)
    
    #add the firts convolution layer
    first_conv_layer, weights_conv1 = \
        add_convolution_layer(input=x_image,
                       num_input_channels=num_channels,
                       kernel_size=kernel_size1,
                       number_kernels=number_kernels1,
                       use_pooling=True)
    
    #add the second Convolutional Layers
        
    second_conv_layer, weights_conv2 = \
        add_convolution_layer(input=first_conv_layer,
                       num_input_channels=number_kernels1,
                       kernel_size=kernel_size2,
                       number_kernels=number_kernels2,
                       use_pooling=True)
    
    '''flatten the output of the second convolution layer'''
    output_flatten_layer, num_features = flatten_layer(second_conv_layer)
    

    #Add a fully-connected layer to the network.
    layer_fc1,weights_fc1 = add_fully_connected_layer(input=output_flatten_layer,
                             num_inputs=num_features,
                             num_outputs=fc_size,
                             output_layer=False)
    
    
    """
    #############################################################################
    Add another fully-connected layer that outputs vectors of length num_classes 
    for determining which of the classes the input image belongs to. 
    ##############################################################################
    """
    
    layer_fc2,weights_fc2 = add_fully_connected_layer(input=layer_fc1,num_inputs=fc_size,num_outputs=num_train_classes,output_layer=True)
    y_pred = tf.nn.softmax(layer_fc2)
    y_pred_cls = tf.argmax(y_pred, axis=1)
    
    '''add cross entropy loss at the end of softmax for optimization'''
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(logits=layer_fc2,labels=y_true)
    cost = tf.reduce_mean(cross_entropy)
    optimizer = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(cost)
    
    ''' Evaluate the performance metric using accuracy measure'''
    correct_prediction = tf.equal(y_pred_cls, y_true_cls)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    
    
    """
    Create TensorFlow session
    """
    session = tf.Session()
    
    #initialize weight and bias and 
    session.run(tf.global_variables_initializer())

    start_training_evaluating(n_it)
    #plot the training  accuracy vs validation accuracy
    plot_accuracy_loss()
    #plot activations of the first, and second convolution layers as illustrated &
    plot_activation_of_conv_layer()
    

    #plot histogram of weights
    plot_histogram_of_weights()
    
    session.close()
    
    
    