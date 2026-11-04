# Human review: প্রথম calibration round

Status: READY FOR INDEPENDENT REVIEW. Human responses: NOT COLLECTED.

এই pack-এ পুরোনো pilot-এর আটটি prompt আছে। উদ্দেশ্য হলো prompt থেকে কী চাওয়া হয়েছে এবং gold-check কী হওয়া উচিত তা স্বাধীনভাবে বোঝা। এগুলো নতুন held-out benchmark নয়। Model-এর output বা আমাদের checker-এর প্রত্যাশা দেওয়া হয়নি।

## কীভাবে কাজ করবেন

1. Reviewer A ও B নিজের নিজের file আলাদাভাবে পূরণ করবেন। প্রথম round শেষ হওয়ার আগে উত্তর আলোচনা করবেন না এবং পুরোনো gold/checker/result দেখবেন না।
2. কোনো case আগে দেখে থাকলে prior exposure লিখবেন। ইতিমধ্যে জানা label ভুলে যাওয়ার ভান করার প্রয়োজন নেই; এই কারণে সম্পূর্ণ blind study দাবি করা হবে না।
3. প্রতিটি prompt পড়ে purpose লিখবেন: analogy / requirement / counter-example / mixed / unclear। কোনো example প্রাসঙ্গিক না হলে সেটিও লিখবেন।
4. MUST USE, MAY USE, MUST NOT USE আলাদা করুন। প্রতিটি বাধ্যবাধকতা বা নিষেধাজ্ঞার পক্ষে prompt-এর একটি ছোট quote দিন। স্পষ্ট নির্দেশ, reasonable inference ও uncertain interpretation আলাদা করে লিখুন।
5. Prompt-এ নিষেধ না থাকলে নিজের পছন্দকে gold prohibition করবেন না। একটি negative example-এর সব বৈশিষ্ট্যই নিষিদ্ধ ধরে নেবেন না।
6. মূল task-এর কোন শর্ত বজায় থাকবে, conflict আছে কি না এবং গ্রহণযোগ্য একাধিক উত্তর সম্ভব কি না লিখুন। সময় লাগলে পূর্ণ code লিখতে হবে না; গ্রহণযোগ্য behaviour বা ছোট output sketch যথেষ্ট।
7. Accept / revise / exclude verdict দিন। সংশোধন প্রয়োজন হলে কী স্পষ্ট করতে হবে লিখুন; original prompt বদলে নিজের interpretation বসাবেন না।

প্রথম round-এ প্রায় ৩০–৪৫ মিনিট রাখুন; প্রকৃত সময় record করুন। বেশি সময় লাগলে সেটিও data-construction cost হিসেবে গুরুত্বপূর্ণ।

## Round শেষে

দুই file জমা হওয়ার পরে researcher-only mapping খুলে adjudication.md-তে মতভেদ লিখবেন। আগে দেওয়া উত্তর অপরিবর্তিত রেখে পাশে final decision যোগ করবেন। Free-text উত্তর থেকে স্বয়ংক্রিয় exact agreement হিসাব করা হবে না; প্রথমে atomic scope/constraint statements align করতে হবে। Raw disagreement, exclusion/revision এবং final labels আলাদা থাকবে। আটটি case থেকে স্থিতিশীল population agreement বা final dataset quality দাবি করা যাবে না।

এই calibration-এর পরে guide সংশোধন করে নতুন seed-এ independent annotation শুরু হবে। Human availability নিশ্চিত; annotation completion এবং agreement এখনও pending।
