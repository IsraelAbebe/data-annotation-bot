import telebot


import pandas as pd
import telebot
from telebot import types


file_name = 'data/test.csv'

def read_csv(file_name,user_name):
    data = pd.read_csv(file_name)
    data[user_name] = np.nan
    return data


def update_csv(file_name, image_id, choice,user_name):
    # print('updating')
    df = pd.read_csv(file_name)
    df.loc[df['ID'] == image_id, user_name] = choice
    df.to_csv(file_name, index=False)


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    images_df = read_csv(file_name)
    # print(images_df.head())
    if images_df.empty:
        bot.send_message(chat_id=message.chat.id, text="All images have been shown.")
    else:
        unshown_images = images_df.loc[images_df[user_name].isnull()]
        if unshown_images.empty:
            bot.send_message(chat_id=message.chat.id, text="All images have been shown.")
        else:
            unshown_images = unshown_images.sample(frac=1).reset_index(drop=True) # shuffle the dataframe and reset index
            image = unshown_images.iloc[0]
            keyboard = types.InlineKeyboardMarkup()
            yes_button = types.InlineKeyboardButton("Yes", callback_data=f'yes_{image["ID"]}')
            no_button = types.InlineKeyboardButton("No", callback_data=f'no_{image["ID"]}')
            keyboard.add(yes_button, no_button)
            bot.send_photo(chat_id=message.chat.id, photo=open(image['image'], 'rb'), caption=image['description'], reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data.startswith('yes_'))
def callback_yes(call):
    user_name = call.message.chat.first_name
    image_id = call.data.split('_')[1]
    update_csv(file_name, int(image_id), choice='yes',user_name=user_name)
    bot.send_message(chat_id=call.message.chat.id, text=f"Thank you for your response! {user_name}")
    start(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('no_'))
def callback_no(call):
    user_name = call.message.chat.first_name
    image_id = call.data.split('_')[1]
    update_csv(file_name, int(image_id), choice='no',user_name=user_name)
    bot.send_message(chat_id=call.message.chat.id, text=f"Thank you for your response! {user_name}")
    start(call.message)



bot.polling()