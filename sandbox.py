#!/usr/bin/env python
# coding: utf-8

# In[7]:


from dotenv import dotenv_valueso


# In[8]:


config = dotenv_values('.env')


# In[9]:


config


# In[10]:


config['HOST_NODE_IP']


# In[12]:


int(config['HOST_NODE_PORT'])


# In[ ]:




