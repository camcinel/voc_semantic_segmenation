import torch.nn as nn



class Conv(nn.Module):
    def __init__(self, in_dim=None, out_dim=None):
        super().__init__()
        
        self.sequence = nn.Sequential(
            nn.Conv2d(in_dim, out_dim, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(out_dim)
            )

    def forward(self, x):
        return self.sequence(x)

class deConv(nn.Module):
    def __init__(self, in_dim=None, out_dim=None, kernel_size=2, stride=2):
        super().__init__()
        
        self.sequence = nn.Sequential(
            nn.ConvTranspose2d(in_dim, out_dim, kernel_size=kernel_size, stride=stride),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(out_dim)
            )

    def forward(self, x):
        return self.sequence(x)

class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.relu = nn.ReLU(inplace=True)

        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x = self.bn1(self.relu(self.conv1(x)))
        x = self.bn2(self.relu(self.conv2(x)))
        return x

# ToDO Fill in the __ values
class FCN8(nn.Module):

    def __init__(self, n_class):
        super().__init__()
        self.n_class = n_class

        # Convolution layers
        self.conv1 = DoubleConv(3, 64)           #(64,224,224)       
       
        self.mpool= nn.MaxPool2d(2, 2, 0)          #(64,112,112)

        self.conv2 = DoubleConv(64, 128)   #(128, 112,112)

        # self.mpool2 = nn.MaxPool2d(2, 2, 0)         #(128,56,56)

        self.conv3 = nn.Sequential(DoubleConv(128, 256), Conv(256, 256))    #(256,56,56)

        # self.mpool3 = nn.MaxPool2d(2, 2, 0)          #(256,28,28)

        self.conv4 = nn.Sequential(DoubleConv(256, 512), Conv(512, 512))    #(512,28,28)

        # self.mpool4 = nn.MaxPool2d(2, 2, 0)          #(512,14,14)

        self.conv5 = nn.Sequential(DoubleConv(512, 512), Conv(512, 512))    #(512,14,14)

        # self.mpool5 = nn.MaxPool2d(2, 2, 0)          #(512,7,7)

        self.conv6 = DoubleConv(512, 4096)           #(4096,7,7)

        self.conv7 = Conv(4096, self.n_class)        #(n_class,7,7)

        self.conv8 = Conv(512, self.n_class)
        self.conv9 = Conv(256, self.n_class)
        self.conv10 = Conv(128, self.n_class)
        self.conv11 = Conv(64, self.n_class)

        # Deconvolution layers
        self.deconv = deConv(self.n_class, self.n_class)     #(n_class,14,14)
        # self.deconv2 = deConv(self.n_class, self.n_class)     #(n_class,28,28)
        # self.deconv3 = deConv(self.n_class, self.n_class)     #(n_class,56,56)
        # self.deconv4 = deConv(self.n_class, self.n_class)     #(n_class,112,112)
        # self.deconv5 = deConv(self.n_class, self.n_class)     #(n_class,224,224)



    def forward(self, x):
        out1 = self.conv1(x)                               #(64,224,224)
        out2 = self.conv2(self.mpool(out1))                #(128,112,112)
        out3 = self.conv3(self.mpool(out2))                #(256,56,56)
        out4 = self.conv4(self.mpool(out3))                #(512,28,28)
        out5 = self.conv5(self.mpool(out4))                #(512,14,14)
        out6 = self.conv6(self.mpool(out5))                #(4096,7,7)
        out7 = self.conv7(out6)                            #(n_class,7,7)

        out8 = self.deconv(out7)                                      #(n_class,14,14)
        out9 = self.deconv(out8 + self.conv8(self.mpool(out4)))       #(n_class,28,28)
        out10 = self.deconv(out9 + self.conv9(self.mpool(out3)))      #(n_class,56,56)
        out11 = self.deconv(out10 + self.conv10(self.mpool(out2)))    #(n_class,112,112)
        y = self.deconv(out11 + self.conv11(self.mpool(out1)))    #(n_class,224,224)

        return y  # size=(N, n_class, H, W)
