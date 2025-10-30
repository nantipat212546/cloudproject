BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "favorites" (
	"id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"recipe_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("recipe_id") REFERENCES "recipes"("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "recipes" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(100) NOT NULL,
	"ingredients"	TEXT NOT NULL,
	"instructions"	TEXT NOT NULL,
	"image"	VARCHAR(200),
	"user_id"	INTEGER NOT NULL,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"username"	VARCHAR(50) NOT NULL,
	"password"	VARCHAR(200) NOT NULL,
	PRIMARY KEY("id"),
	UNIQUE("username")
);
INSERT INTO "favorites" VALUES (1,1,1);
INSERT INTO "recipes" VALUES (1,'ต้มยำกุ้ง','กุ้ง, ตะไคร้, ใบมะกรูด, มะนาว, เห็ด','1. ต้มน้ำ + ตะไคร้ + ใบมะกรูด 2. ใส่กุ้ง + เห็ด ต้ม 5 นาที 3. ปรุงรสด้วยมะนาว + น้ำปลา เสิร์ฟร้อน','5c08e33a0ebb480ea9dd4d941c298724.jpg',1);
INSERT INTO "recipes" VALUES (2,'ผัดไทยกุ้ง','ก๋วยเตี๊ยว, กุ้ง, ถั่วงอก, ไข่, น้ำมะขาม','1. ผัดกุ้ง + ไข่ 2. ใส่ก๋วยเตี๊ยว + ถั่วงอก 3. ปรุงรสด้วยน้ำมะขาม + น้ำตาลทรายแดง คลุกให้เข้า ไม่ใส่ซีอิ๊ว','4fa7c10d469e40cabdf77020283f4a95.jpg',1);
INSERT INTO "recipes" VALUES (3,'แกงเขียวหวานไก่','ไก่, พริกแกงเขียวหวาน, กะทิ, มะเขือ, ใบโหระพา','1. ผัดพริกแกงกับกะทิ 2. ใส่ไก่ + มะเขือ ต้ม 10 นาที 3. ใส่ใบโหระพา ปิดไฟ','76aea6814a29402684fc67b07e130ec7.jpg',1);
INSERT INTO "recipes" VALUES (4,'ผัดกะเพราไก่','ไก่สับ, ใบกะเพรา, พริก, กระเทียม, น้ำปลา','1. ผัดกระเทียม + พริก 2. ใส่ไก่สับ ผัดสุก 3. ใส่ใบกะเพรา + น้ำปลา ผัดเร็ว ๆ เสิร์ฟกับข้าว','a29022b4355a47c5a019d62690d34178.jpg',1);
INSERT INTO "recipes" VALUES (5,'ข้าวผัดกุ้ง','ข้าวสวย, กุ้ง, ไข่, ต้นหอม, น้ำปลา','1. ผัดไข่ + กุ้ง 2. ใส่ข้าว + ต้นหอม 3. ปรุงรสด้วยน้ำปลา + น้ำตาล คลุกให้ร้อน','ba53107b3042460aa23361e04323e13f.jpg',1);
INSERT INTO "recipes" VALUES (6,'ต้มยำไก่','ไก่, ตะไคร้, ข่า, ใบมะกรูด, มะนาว','1. ต้มน้ำ + ข่า + ตะไคร้ + ใบมะกรูด 2. ใส่ไก่ ต้มสุก 3. ปรุงรสด้วยมะนาว + พริก + น้ำปลา','2b167e2818924513ae4b99a401d2f3e3.jpg',1);
INSERT INTO "recipes" VALUES (7,'แกงส้มปลาช่อน','ปลาช่อน, พริกแกงส้ม, มะนาว, ผักรวม, น้ำปลา','1. ต้มพริกแกงส้ม 2. ใส่ปลาช่อน + ผักรวม 3. ปรุงรสด้วยมะนาว + น้ำปลา ต้ม 5 นาที','19621f013f6d4cc69ada4ad63ce837de.jpg',1);
INSERT INTO "recipes" VALUES (8,'ส้มตำไทย','มะละกอดิบ, ถั่วฝักยาว, มะเขือเทศ, พริก, มะนาว','1. โขลกพริก + กระเทียม 2. ใส่มะละกอ + ถั่วฝักยาว + มะเขือเทศ 3. ปรุงรสด้วยมะนาว + น้ำปลา + น้ำตาล','93787180f53c451dbf2bdc7e6c0b5490.jpg',1);
INSERT INTO "recipes" VALUES (9,'ไข่เจียว','ไข่, ต้นหอม, ถั่วงอก, น้ำปลา','1. ตีไข่ + ต้นหอม + น้ำปลา 2. ใส่น้ำมันร้อน เจียวกรอบ 3. ใส่ถั่วงอก ติดกัน เสิร์ฟร้อน','f60e85db70dd415891195b90304e138c.jpg',1);
INSERT INTO "recipes" VALUES (10,'ยำวุ้นเส้นทะเล','วุ้นเส้น, กุ้ง, ปลาหมึก, มะนาว, พริก, หอมแดง','1. ลวกวุ้นเส้น + กุ้ง + ปลาหมึก 2. ผสมหอมแดง + พริก 3. ปรุงรสด้วยมะนาว + น้ำปลา คลุกให้เข้า','0bdb562dab254154becff940ed812930.jpg',1);
INSERT INTO "users" VALUES (1,'Donald','scrypt:32768:8:1$CAW7PIueLdCn8uXQ$5898a11d1cad879ecfc13ee52ff8a5c5d92f76266abab0a7999002d684be580dfffc71a2b98036c6a9a793aa52c3d9faa52e6f11eb192e852f7768d227453aa8');
COMMIT;
