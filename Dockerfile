FROM nvidia/cuda:11.0.3-devel-ubuntu18.04

WORKDIR /tools

# install general dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
    git \
    vim \
    cmake \
    build-essential \
    software-properties-common \
    python3-dev \
    python3-pip \
    python3-packaging \
    libboost-program-options-dev \
    libboost-filesystem-dev \
    libboost-graph-dev \
    libboost-regex-dev \
    libboost-system-dev \
    libboost-test-dev \
    libeigen3-dev \
    libsuitesparse-dev \
    libfreeimage-dev \
    libmetis-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libglew-dev \
    qtbase5-dev \
    libqt5opengl5-dev \
    libcgal-dev \
    libatlas-base-dev \
    libfreetype6-dev \
    && add-apt-repository ppa:ubuntugis/ppa \
    && apt-get update && apt-get install -y \
    #VisSat
    gdal-bin \
    libgdal-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && pip3 install --upgrade pip

WORKDIR /tools

# install ceres-solver
RUN git clone -b 2.1.0 https://ceres-solver.googlesource.com/ceres-solver
WORKDIR /tools/ceres-solver/build
RUN cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && make -j8 && make install

# install colmap
WORKDIR /tools
RUN git clone -b 3.7 https://github.com/colmap/colmap && \
    git clone https://github.com/SBCV/ColmapForVisSatPatched.git
WORKDIR /tools/colmap
RUN git checkout 31df46c6c82bbdcaddbca180bc220d2eab9a1b5e
RUN bash /tools/ColmapForVisSatPatched/apply_patches.sh /tools/colmap
WORKDIR /tools/colmap/build
RUN cmake .. -DGUI_ENABLED=ON -DCUDA_ARCHS=Auto && make -j8 && make install

# VisSat
ENV CPLUS_INCLUDE_PATH /usr/include/gdal
ENV C_INCLUDE_PATH /usr/include/gdal

WORKDIR /home
RUN git clone https://github.com/Kai-46/VisSatSatelliteStereo.git

WORKDIR /tools
RUN apt-get update && apt-get install -y python3-packaging && pip3 install --upgrade pip
RUN pip3 install \
    GDAL==2.2.3 \
    lxml==4.6.3 \
    matplotlib==3.0.0 \
    numba==0.41.0 \
    numpy==1.15.4 \
    Pillow==8.2.0 \
    scipy==1.1.0 \
    utm==0.4.2 \
    imageio==2.5.0 \
    opencv-python==4.1.2.30 \
    pyquaternion==0.9.5 \
    pymap3d==1.7.15 \
    python-dateutil==2.8.0 \
    pyzmq==18.1.1 \
    notebook==5.7.15 \
    open3d-python==0.6.0.0 \
    numpy-groupies \
    pyproj==2.4.0

# remove unneeded files
#RUN rm -rf /tools



# RUN mkdir /home
RUN chmod -R 777 /home
ENV HOME /home
WORKDIR /home

