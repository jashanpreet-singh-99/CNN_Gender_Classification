import os
import random
import cv2 as cv

male_count = 0
female_count = 0
print("""
c : For classification (Filtered to F_Data)
s : For Swaping (F_Data to F_Data)
f : For Final (F_Data to Final_Data_###)
t : For 50 Test Data
""")
ch = input("Selection : ")

if ch == 'c' :
    files = os.listdir('filtered_faces/')

    print(len(files))
    for file in files :
        img = cv.imread('filtered_faces/' + file)
    
        while True:
            k = cv.waitKey(1)
            print(k)
            if k == ord('m') :
                cv.imwrite("F_Data/M_" + str(male_count) + '.png', img)
                male_count += 1
                cv.destroyAllWindows()
                break;
            elif k == ord('f') :
                cv.imwrite("F_Data/F_" + str(female_count) + '.png', img)
                female_count += 1
                cv.destroyAllWindows()
                break;
            cv.imshow('img', img)
    print("End")
elif ch == 's':
    """
    Recheck the script fix the male ad femle cout error while swapping
    """
    files = os.listdir('classified_images_##/')
    print('Swap zone Entered')
    male_list = [x for x in files if 'M' in x]
    female_list = [x for x in files if 'F' in x]
    
    

    male_maxed = [(x.split('_')[1]).split('.')[0] for x in files if 'M' in x]
    female_maxed = [(x.split('_')[1]).split('.')[0] for x in files if 'F' in x]
    male_maxed = list(map(int, male_maxed))
    female_maxed = list(map(int, female_maxed))

    print("Male Max   : ",max(male_maxed))
    print("Female_Max : ",max(female_maxed))

    male_count = max(male_maxed) + 1
    female_count = max(female_maxed) + 1

    print("Male List :", len(male_list))
    print("Female List :", len(female_list))

    ch = input("Select Gender : ")

    if ch == 'm' :
        cursor = 0
        ch = eval(input("Jump to cursor : "))
        if ch > 0 :
            cursor = ch
        print("Starting for male : ")

        while cursor < male_count :
            file = male_list[cursor]
            try :
                img = cv.imread('classified_images_##/' + file)
            except :
                cursor += 1
                continue
            while True:
                k = cv.waitKey(1)
                if k != -1 :
                    print(k, " : VaL : ", cursor, " ORG : ", file)
                if k == ord('s') :
                    cv.imwrite("classified_images_##/F_" + str(female_count) + '.png', img)
                    female_count += 1
                    cursor += 1
                    os.remove("classified_images_##/" + file)
                    cv.destroyAllWindows()
                    break;
                if k == ord('n') :
                    cursor += 1
                    cv.destroyAllWindows()
                    break;
                if k == ord('b') :
                    cursor -= 1
                    cv.destroyAllWindows()
                    break;
                cv.imshow('img', img)
        
    elif ch == 'f':
        cursor = 0
        ch = eval(input("Jump to cursor : "))
        if ch > 0 :
            cursor = ch
        print("Starting for Female : ")

        while cursor < female_count :
            file = female_list[cursor]
            try :
                img = cv.imread('classified_images_##/' + file)
            except :
                cursor += 1
                print("Error in reading image.")
                continue
            while True:
                k = cv.waitKey(1)
                if k != -1 :
                    print(k, " : VaL : ", cursor, " ORG : ", file)
                if k == ord('s') :
                    cv.imwrite("classified_images_##/M_" + str(male_count) + '.png', img)
                    male_count += 1
                    cursor += 1
                    os.remove("classified_images_##/" + file)
                    cv.destroyAllWindows()
                    break;
                if k == ord('n') :
                    cursor += 1
                    cv.destroyAllWindows()
                    break;
                if k == ord('b') :
                    cursor -= 1
                    cv.destroyAllWindows()
                    break;
                try :
                    resized_image = cv.resize(img, (512,512))
                    cv.imshow('img', resized_image)
                except :
                    print("Unable to show image.")
                    cursor += 1
                    break;
    else :
        print("cool")
            
elif ch == 'f' :
    path = 'classified_images_##_##/'
    files = os.listdir('classified_images_##/')
    
    male_list = [x for x in files if 'M' in x]
    female_list = [x for x in files if 'F' in x]
    
    male_count = len(male_list)
    female_count = len(female_list)

    male_range = random.sample(range(0, male_count), 4500)
    female_range = random.sample(range(0, female_count), 4500)
    cursor = 0
    while cursor < len(male_range):
        file = male_list[male_range[cursor]]
        img = cv.imread('classified_images_##/' + file)
        cv.imwrite(path + 'M_' + str(cursor) + '.png', img)
        print("Male : ", cursor)
        cursor += 1
    cursor = 0
    while cursor < len(female_range):
        file = female_list[female_range[cursor]]
        img = cv.imread('classified_images_##/' + file)
        cv.imwrite(path + 'F_' + str(cursor) + '.png', img)
        print("Female : ", cursor)
        cursor += 1
    print("Done")
elif ch == 't' :
    path = 'Test_###/'
    files = os.listdir('F_Data/')
    
    male_list = [x for x in files if 'M' in x]
    female_list = [x for x in files if 'F' in x]
    
    male_count = len(male_list)
    female_count = len(female_list)

    male_range = random.sample(range(0, male_count), 50)
    female_range = random.sample(range(0, female_count), 50)
    cursor = 0
    while cursor < len(male_range):
        file = male_list[male_range[cursor]]
        img = cv.imread('F_Data/' + file)
        cv.imwrite(path + 'M_' + str(cursor) + '.png', img)
        print("Male : ", cursor)
        cursor += 1
    cursor = 0
    while cursor < len(female_range):
        file = female_list[female_range[cursor]]
        img = cv.imread('F_Data/' + file)
        cv.imwrite(path + 'F_' + str(cursor) + '.png', img)
        print("Female : ", cursor)
        cursor += 1
    print("Done")
